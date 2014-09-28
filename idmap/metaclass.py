from django.db.models.base import ModelBase


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
