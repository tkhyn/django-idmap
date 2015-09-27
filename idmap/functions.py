from .signals import pre_flush_idmap, post_flush_idmap


def flush(db=None):
    from .models import SharedMemoryModel
    pre_flush_idmap.send(SharedMemoryModel, db=db)
    for model in SharedMemoryModel.__subclasses__():
        model.flush_instance_cache(db=db, flush_sub=True)
    post_flush_idmap.send(SharedMemoryModel, db=db)
