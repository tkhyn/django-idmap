django-idmap
============

An identity mapper for the Django ORM.

A pluggable Django application which allows you to explicitally mark your
models to use an identity mapping pattern. This will share instances of the
same model in memory throughout your interpreter.

Please note, that deserialization (such as from the cache) will *not* use the
identity mapper.

Usage
-----

To use the shared memory model you simply need to inherit from it (instead of
models.Model). This enable all queries (and relational queries) to this model
to use the shared memory instance cache, effectively creating a single instance
for each unique row (based on primary key) in the queryset.

You can chose between 2 caching modes:

- Weak references mode: the instance will be removed from the cache once there
  are no more references to it. This is the default behavior
- Strong references mode: the instance will only be removed from the cache when
  it is flushed

Note that django-idmap clears the cache when the ``request_finished`` or
``post_syncdb`` signal is sent. This default behavior can be modified by
disconnecting the flush_cache function from these signals.


Examples
--------

If you want to simply mark all of your models as a SharedMemoryModel, you might
as well just import it as models.

::

    from idmap import models

    class MyModel(models.SharedMemoryModel):
        name = models.CharField(...)

Because the system is isolated, you may mix and match SharedMemoryModels
with regular Models. The module idmap.models imports everything from
django.db.models and only adds SharedMemoryModel, so you can simply replace
your import of models from django.db.

::

    from idmap import models

    class MyModel(models.SharedMemoryModel):
        name = models.CharField(...)
        fkey = models.ForeignKey('Other')

    class Other(models.Model):
        name = models.CharField(...)

If you want to use strong references for a particular model, simply set
``use_strong_refs`` to ``True`` in the derived model class.

::

   from idmap import models

   class MyModel(models.SharedMemoryModel):
      use_strong_refs = True
      [...]

With strong references, the model will be loaded only once from the database,
until it is explicitly erased from the cache.

You may want to use the functions or class methods:

- ``idmap.flush_cache()`` to erase the whole cache
- ``SharedMemoryModel.flush_instance_cache()`` to erase the cache for one class
- ``SharedMemoryModel.flush_cached_instance(instance)`` to erase one instance from
  the cache

References
----------

Forked from https://github.com/dcramer/django-idmapper

Original code and concept: http://code.djangoproject.com/ticket/17
