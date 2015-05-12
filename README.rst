django-idmap
============

|copyright| 2014-2015 Thomas Khyn
|copyright| 2009 David Cramer

An identity mapper for the Django ORM. This is a fork of django-idmapper_,
which is no longer maintained.

``django-idmap`` works with django 1.8+ and supported python versions (2.7,
3.3, 3.4)


What is it?
-----------

``django-idmap`` is a Django application which:
- loads only once the instances in memory the first time they are needed
- share them througout your interpreter until the request is finished

Indeed, the default django behavior is to expose different instances for the
same database entry between the start and the end of the request. It has one
main consequence: the temporary attributes you may set are lost if you want
to access the same database object in another place in your code.

.. warning::
   Deserialization (such as from the cache) will *not* use the identity mapper.


Installation
------------

As straightforward as it can be, using pip::

   pip install django-idmap

As ``django-idmap`` does not expose any ``Model`` nor management command, you
do not need to add it to your ``INSTALLED_APPS`` setting.


Usage
-----

To use the exposed shared memory model you simply need to inherit from it
(instead of ``models.Model``). This enable all queries (and relational queries)
to this model to use the shared memory instance cache, effectively creating a
single instance for each unique row (based on primary key) in the queryset.

You can chose between 2 caching modes:

- Weak references mode: the instance will be removed from the cache once there
  are no more references to it. This is the default behavior
- Strong references mode: the instance will only be removed from the cache when
  it is flushed

Note that ``django-idmap`` clears the cache when the ``request_finished`` or
``post_syncdb`` signal is sent. This default behavior can be modified by
disconnecting the exposed ``idmap.flush_cache`` function from these signals.


Examples
--------

You can import ``idmap.models`` as you would import ``django.db.models``.
``idmap.models`` exposes all what is exposed by ``django.db.models`` plus the
``SharedMemoryModel`` model class.

You may mix and match SharedMemoryModels with regular Models::

    from idmap import models

    class MyModel(models.SharedMemoryModel):
        name = models.CharField(...)
        fkey = models.ForeignKey('Other')

    class Other(models.Model):
        name = models.CharField(...)

If you want to use strong references for a particular model, simply set
``use_strong_refs`` to ``True`` in the derived model class::

   from idmap import models

   class MyModel(models.SharedMemoryModel):
      use_strong_refs = True
      [...]

With strong references, the model will be loaded only once from the database,
until it is explicitly erased from the cache.

You may want to use the functions or class methods:

- ``idmap.flush_cache()`` to erase the whole cache
- ``SharedMemoryModel.flush_instance_cache()`` to erase the cache for one model
- ``SharedMemoryModel.flush_cached_instance(instance)`` to erase one instance
  from the cache


Multiple database support (new in version 1.0)
----------------------------------------------

In some cases, you may need to store instances of the same model in several
databases. It is possible to tell ``django-idmap`` to also take the database
into account when creating or getting instances::

   class MyModel(models.SharedMemoryModel):
      multi_db = True
      [...]

This way, ``instance1_1`` with primary key ``1`` in database ``db1`` will be
different from ``instance2_1`` with primary key ``1`` in database ``db2``::

   >>> MyModel.objects.using('db1').create(pk=1)
   >>> MyModel.objects.using('db2').create(pk=1)
   >>> idmap.flush_cache()
   >>> instance1_1 = MyModel.objects.using('db1').get(pk=1)
   >>> instance2_1 = MyModel.objects.using('db2').get(pk=1)
   >>> assert instance1_1 is instance 2_1
   AssertionError


References
----------

David Cramer's django-idmapper_

Original code and concept: http://code.djangoproject.com/ticket/17

.. |copyright| unicode:: 0xA9
.. _django-idmapper: https://github.com/dcramer/django-idmapper
