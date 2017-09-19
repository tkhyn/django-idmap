from django.db.models.query import QuerySet
from django.utils import six

try:
    # django 1.9+
    from django.db.models.query import ModelIterable, ValuesIterable, \
        ValuesListIterable, FlatValuesListIterable
    HAS_ITER_CLASSES = True
except ImportError:
    # django 1.8
    from django.db.models.query import ValuesQuerySet, ValuesListQuerySet
    HAS_ITER_CLASSES = False


class IdMapQuerySet(QuerySet):

    def get(self, *args, **kwargs):
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
        try:
            if len(args) == 1:
                q = args[0]
                if q.connector == 'AND' and not q.negated and \
                len(q.children) == 1:
                    c = q.children[0]
                    if c[0] in pk_interceptions:
                        args = []
                        for k in pk_interceptions:
                            kwargs.pop(k, None)
                        kwargs[pk_attr] = c[1]
        except (AttributeError, IndexError):
            pass

        if len(kwargs) == 1 and next(six.iterkeys(kwargs)) in pk_interceptions:
            instance = self.model.get_cached_instance(
                next(six.itervalues(kwargs)), db)

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
            if HAS_ITER_CLASSES:
                kw = {'_iterable_class': ModelIterable}
            else:
                # django 1.8 does not use iterable classes
                kw = {'klass': QuerySet}

            clone = self._clone(_fields=None, **kw)
            clone.query.clear_select_fields()
            clone.query.default_cols = True

            if HAS_ITER_CLASSES:
                instance = super(
                    IdMapQuerySet,
                    clone
                ).get(*args, **kwargs)
            else:
                instance = clone.get(*args, **kwargs)

            # gets the pk of the retrieved object, and if it exists in the
            # cache, returns the cached instance
            # This enables object retrieved from 2 different ways (e.g directly
            # and through a relation) to share the same instance in memory.
            cached_instance = self.model.get_cached_instance(instance.pk, db)
            if cached_instance is not None:
                instance = cached_instance

        if HAS_ITER_CLASSES:
            # django 1.9+
            if self._iterable_class is ModelIterable:
                return instance
            elif self._iterable_class is ValuesListIterable:
                return [getattr(instance, f) for f in self._fields]
            elif self._iterable_class is FlatValuesListIterable:
                return getattr(instance, self._fields[0])
            elif self._iterable_class is ValuesIterable:
                return {f: getattr(instance, f) for f in self._fields}
        else:
            if isinstance(self, ValuesListQuerySet):
                values = [getattr(instance, f) for f in self._fields]
                if self.flat:
                    return values[0]
                else:
                    return values
            elif isinstance(self, ValuesQuerySet):
                return {f: getattr(instance, f) for f in self._fields}
            else:
                return instance
