from django.db.models.query import QuerySet
from django.utils import six


class IdMapQuerySet(QuerySet):

    def get(self, **kwargs):
        instance = None
        pk_attr = self.model._meta.pk.attname
        db = self._db or self.db

        pk_interceptions = (
            'pk',
            'pk__exact',
            pk_attr,
            '%s__exact' % pk_attr
        )

        # This is an exact lookup for the pk only -> kwargs.values()[0]
        # is the pk
        if len(kwargs) == 1 and next(six.iterkeys(kwargs)) in pk_interceptions:
            pk = list(kwargs.values())[0]
            instance = self.model.get_cached_instance(pk, db)

        where_children = self.query.where.children

        if len(where_children) == 1:
            where_child = where_children[0]
            col = where_child.lhs.target.column
            lookup_type = where_child.lookup_name
            param = where_child.rhs

            if col in ('pk', pk_attr) and lookup_type == 'exact':
                instance = self.model.get_cached_instance(param, db)

        # The cache missed or was not applicable, hit the database!
        if instance is None:
            instance = super(IdMapQuerySet, self).get(**kwargs)

            # gets the pk of the retrieved object, and if it exists in the
            # cache, returns the cached instance
            # This enables object retrieved from 2 different ways (e.g directly
            # and through a relation) to share the same instance in memory.
            cached_instance = self.model.get_cached_instance(instance.pk, db)
            if cached_instance is not None:
                return cached_instance

        return instance
