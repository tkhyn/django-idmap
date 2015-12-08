from django.db import models
from django.utils import six

from django.core.signals import request_finished
from django.db.models.signals import pre_delete, post_syncdb

from .manager import SharedMemoryManager

from . import tls  # thread local storage
tls.init_idmap()


class SharedMemoryModel(six.with_metaclass(SharedMemoryModelBase, models.Model)):
    """
    Abstract class to derive any shared memory model from

    :ivar use_strong_refs: should one use strong refs or not for instances.
        False by default. If True, instances will be kept in the cache until
        explicitly flushed
    """

    objects = SharedMemoryManager()

    use_strong_refs = False

    class Meta:
        # does not inherit from base_class.Meta but that's not an issue
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

        pk_position = getattr(cls._meta, 'pk_pos', None)
        if pk_position is None:
            # the pk position could not be extracted from _meta
            # calculate it ...
            pk_position = cls._meta.fields.index(pk)
            # ... and store it
            setattr(cls._meta, 'pk_pos', pk_position)

        if len(args) > pk_position:
            # if it's in the args, we can get it easily by index
            result = args[pk_position]
        elif pk.attname in kwargs:
            # retrieve the pk value. Note that we use attname instead of name,
            # to handle the case where the pk is a ForeignKey.
            result = kwargs[pk.attname]
        elif pk.name != pk.attname and pk.name in kwargs:
            # ok we couldn't find the value, but maybe it's a FK and we can
            # find the corresponding object instead
            result = kwargs[pk.name]

        if result is not None and isinstance(result, models.Model):
            # if the pk value happens to be a model instance (which can
            # happen with a FK), we'd rather use its own pk as the key
            result = result._get_pk_val()
        return result

    @classmethod
    def get_cached_instance(cls, pk):
        """
        Method to retrieve a cached instance by pk value. Returns None when
        not found (which will always be the case when caching is disabled for
        this class). Please note that the lookup will be done even when
        instance caching is disabled.
        """
        return tls.get_cached_instance(cls, pk)

    @classmethod
    def _init_instance_cache(cls):
        tls.create_cache(cls, reset=True)

    @classmethod
    def cache_instance(cls, instance):
        """
        Method to store an instance in the cache.
        """
        pk = instance._get_pk_val()
        if pk is not None:
            tls.cache_instance(cls, instance, pk)

    @classmethod
    def _flush_cached_by_key(cls, key):
        try:
            tls.flush_cache_key(cls, key)
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
