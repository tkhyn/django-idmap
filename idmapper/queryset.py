from django.db.models.query import QuerySet

class SharedMemoryQuerySet(QuerySet):
    def get(self, **kwargs):
        instance = None
        pk_interceptions = (
            'pk',
            'pk__exact',
            self.model._meta.pk.attname,
            '%s__exact' % self.model._meta.pk.attname
        )

        # This is an exact lookup for the pk only -> kwargs.values()[0] is the pk
        if len(kwargs) == 1 and kwargs.keys()[0] in pk_interceptions:
            instance = self.model.get_cached_instance(kwargs.values()[0])

        # The cache missed or was not applicable, hit the database!
        if instance is None:
            instance = super(SharedMemoryQuerySet, self).get(**kwargs)

        return instance
