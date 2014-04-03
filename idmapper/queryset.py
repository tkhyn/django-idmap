from django.db.models.query import QuerySet


class SharedMemoryQuerySet(QuerySet):
    def get(self, **kwargs):
        instance = None
        pk_attr = self.model._meta.pk.attname

        pk_interceptions = (
            'pk',
            'pk__exact',
            pk_attr,
            '%s__exact' % pk_attr
        )

        # This is an exact lookup for the pk only -> kwargs.values()[0] is the pk
        if len(kwargs) == 1 and kwargs.keys()[0] in pk_interceptions:
            instance = self.model.get_cached_instance(kwargs.values()[0])

        where_children = self.query.where.children

        if len(where_children) == 1:
            [(field, lookup_type, _, param)] = where_children

            if field.col in ('pk', pk_attr) and lookup_type == 'exact':
                instance = self.model.get_cached_instance(param)

        # The cache missed or was not applicable, hit the database!
        if instance is None:
            instance = super(SharedMemoryQuerySet, self).get(**kwargs)

        return instance
