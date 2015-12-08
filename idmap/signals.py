from django.core.signals import request_finished
from django.db.models.signals import pre_delete, post_migrate


# Flush cache after syncdb
def flush_cache(**kwargs):
    from .models import SharedMemoryModel
    for model in SharedMemoryModel.__subclasses__():
        model.flush_instance_cache(flush_sub=True)

request_finished.connect(flush_cache)
post_migrate.connect(flush_cache)


# Remove instance from cache upon deletion
def flush_cached_instance(sender, instance, **kwargs):
    # XXX: Is this the best way to make sure we can flush?
    if not hasattr(instance, 'flush_cached_instance'):
        return
    sender.flush_cached_instance(instance)
pre_delete.connect(flush_cached_instance)
