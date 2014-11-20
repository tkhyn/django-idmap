from django.db.models.query import QuerySet
from django.utils import six


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

        # This is an exact lookup for the pk only -> kwargs.values()[0]
        # is the pk
        if len(kwargs) == 1 and next(six.iterkeys(kwargs)) in pk_interceptions:
            instance = self.model.get_cached_instance(kwargs.values()[0])

        where_children = self.query.where.children

        if len(where_children) == 1:
            try:
                # Django 1.7+
                where_child = where_children[0]
                col = where_child.lhs.target.column
                lookup_type = where_child.lookup_name
                param = where_child.rhs
            except AttributeError:
                # in Django 1.6, where_child is the tuple we're after, in 1.4
                # and 1.5, we need to get to the 'children' attribute
                try:
                    field, lookup_type, __, param = where_child
                except TypeError:
                    field, lookup_type, __, param = where_child.children[0]
                col = field.col

            if col in ('pk', pk_attr) and lookup_type == 'exact':
                instance = self.model.get_cached_instance(param)

        # The cache missed or was not applicable, hit the database!
        if instance is None:
            instance = super(SharedMemoryQuerySet, self).get(**kwargs)

            # gets the pk of the retrieved object, and if it exists in the
            # cache, returns the cached instance
            # This enables object retrieved from 2 different ways (e.g directly
            # and through a relation) to share the same instance in memory.
            cached_instance = self.model.get_cached_instance(instance.pk)
            if cached_instance is not None:
                return cached_instance

        return instance
