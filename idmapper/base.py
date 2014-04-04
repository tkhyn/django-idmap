from weakref import WeakValueDictionary
import threading

from django.core.signals import request_finished
from django.db.models.base import Model, ModelBase
from django.db.models.signals import pre_delete, post_syncdb

from manager import SharedMemoryManager

# thread local storage for instances cache
_tls = threading.local()
_tls.idmapper_cache = {}


class SharedMemoryModelBase(ModelBase):

    def __call__(self, *args, **kwargs):
        """
        This method will either create an instance (by calling the default
        implementation) or try to retrieve one from the class-wide cache by
        infering the pk value from args and kwargs. If instance caching is
        enabled for this class, the cache is populated whenever possible
        (ie when it is possible to infer the pk value).
        """

        def new_instance():
            return super(SharedMemoryModelBase, self).__call__(*args, **kwargs)

        instance_key = self._get_cache_key(args, kwargs)
        # depending on the arguments, we might not be able to infer the PK
        # in that case, we create a new instance
        if instance_key is None:
            return new_instance()

        cached_instance = self.get_cached_instance(instance_key)
        if cached_instance is None:
            cached_instance = new_instance()
            self.cache_instance(cached_instance)

        return cached_instance


class SharedMemoryModel(Model):
    """
    Abstract class to derive any shared memory model from

    :ivar use_strong_refs: should one use strong refs or not for instances.
        False by default. If True, instances will be kept in the cache until
        explicitly flushed
    """

    __metaclass__ = SharedMemoryModelBase
    objects = SharedMemoryManager()

    use_strong_refs = False

    class Meta:
        abstract = True

    @classmethod
    def _get_cache_key(cls, args, kwargs):
        """
        This method is used by the caching subsystem to infer the PK value
        from the constructor arguments. It is used to decide if an instance
        has to be built or is already in the cache.
        """
        result = None
        # Quick hack for my composites work for now.
        if hasattr(cls._meta, 'pks'):
            pk = cls._meta.pks[0]
        else:
            pk = cls._meta.pk
        # get the index of the pk in the class fields. this only needs to be
        # calculated *once*, but isn't at the moment
        # TODO: calculate pk_position only once
        pk_position = cls._meta.fields.index(pk)
        if len(args) > pk_position:
            # if it's in the args, we can get it easily by index
            result = args[pk_position]
        elif pk.attname in kwargs:
            # retrieve the pk value. Note that we use attname instead of name,
            # to handle the case where the pk is a
            # a ForeignKey.
            result = kwargs[pk.attname]
        elif pk.name != pk.attname and pk.name in kwargs:
            # ok we couldn't find the value, but maybe it's a FK and we can
            # find the corresponding object instead
            result = kwargs[pk.name]

        if result is not None and isinstance(result, Model):
            # if the pk value happens to be a model instance (which can
            # happen with a FK), we'd rather use its own pk as the key
            result = result._get_pk_val()
        return result

    @classmethod
    def get_cached_instance(cls, id_):
        """
        Method to retrieve a cached instance by pk value. Returns None when
        not found (which will always be the case when caching is disabled for
        this class). Please note that the lookup will be done even when
        instance caching is disabled.
        """
        if not hasattr(_tls, 'idmapper_cache'):
            return None
        return _tls.idmapper_cache.get(cls, {}).get(id_)

    @classmethod
    def _init_instance_cache(cls):
        new_cache = {} if cls.use_strong_refs else WeakValueDictionary()
        _tls.idmapper_cache[cls] = new_cache

    @classmethod
    def cache_instance(cls, instance):
        """
        Method to store an instance in the cache.
        """
        if instance._get_pk_val() is not None:
            if not cls in _tls.idmapper_cache:
                cls._init_instance_cache()
            _tls.idmapper_cache[cls][instance._get_pk_val()] = instance

    @classmethod
    def _flush_cached_by_key(cls, key):
        try:
            del _tls.idmapper_cache[cls][key]
        except KeyError:
            pass

    @classmethod
    def flush_cached_instance(cls, instance):
        """
        Method to flush an instance from the cache. The instance will always
        be flushed from the cache, since this is most likely called from
        delete(), and we want to make sure we don't cache dead objects.
        """
        cls._flush_cached_by_key(instance._get_pk_val())

    @classmethod
    def flush_instance_cache(cls, flush_sub=False):
        cls._init_instance_cache()
        if flush_sub:
            for s in cls.__subclasses__():
                s.flush_instance_cache(flush_sub=flush_sub)

    def save(self, *args, **kwargs):
        """
        Caches the instance on save
        """
        super(SharedMemoryModel, self).save(*args, **kwargs)
        self.__class__.cache_instance(self)


# Use signals to make sure to catch cascades.

# Flush cache after syncdb
def flush_cache(**kwargs):
    for model in SharedMemoryModel.__subclasses__():
        model.flush_instance_cache(flush_sub=True)
request_finished.connect(flush_cache)
post_syncdb.connect(flush_cache)


# Remove instance from cache upon deletion
def flush_cached_instance(sender, instance, **kwargs):
    # XXX: Is this the best way to make sure we can flush?
    if not hasattr(instance, 'flush_cached_instance'):
        return
    sender.flush_cached_instance(instance)
pre_delete.connect(flush_cached_instance)
