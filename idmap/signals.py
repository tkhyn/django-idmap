"""
Signals are used to automatically flush the idmap cache on finish request,
migrate / syncdb and instance deletion, and to make sure to catch cascades
"""

from django.dispatch import receiver
from django.core.signals import request_finished
from django.db.models.signals import pre_delete, post_syncdb


@receiver((post_syncdb, request_finished))
def flush_cache(**kwargs):
    """
    Flushes the idmap cache on migrate / syncdb and on request end
    """
    from .models import SharedMemoryModel
    for model in SharedMemoryModel.__subclasses__():
        model.flush_instance_cache(flush_sub=True)


@receiver(pre_delete)
def flush_cached_instance(sender, instance, **kwargs):
    """
    Flushes a deleted instance from the idmap cache
    """
    from .models import SharedMemoryModel
    if issubclass(sender, SharedMemoryModel):
        sender.flush_cached_instance(instance)
