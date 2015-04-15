django-idmap - changes
======================


v0.3 (06-10-2014)
-----------------

Added:
- use_strong_refs option
- Django 1.4 to 1.7 compatibility
- Python 3 compatibility

v0.3.3 (16-04-2015)
...................

Added:
- Django 1.8 compatibility

v0.3.2 (21-11-2014)
...................

Fixed:
- Where clause issue on Django 1.4, 1.5 and 1.7

Added:
- already loaded instance are searched even after hitting the database, e.g.
  when making a query on non-pk parameters, for the sake of id consistency

v0.3.1 (06-10-2014)
...................

Fixed:
- use_strong_refs option bug


v0.2 (03-04-2014)
-----------------

- Forked django-idmapper

v0.2.1 (04-04-2014)
...................

Added:
- multi-threading ability (thanks to Andreas Pelme)

Fixed:
- bugs introduced prior to fork
