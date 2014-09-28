import django
from django.db.models import Model
from django.utils import six

from .metaclass import SharedMemoryModelBase


if django.VERSION >= (1, 5):
    base_class = six.with_metaclass(SharedMemoryModelBase, Model)
elif six.PY2:
    class base_class(Model):
        __metaclass__ = SharedMemoryModelBase

        class Meta:
            abstract = True
else:
    raise RuntimeError('Unsupported combination of python and django version')
