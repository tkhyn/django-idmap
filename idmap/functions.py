from .signals import pre_flush, post_flush


def flush(db=None):
    from .models import SharedMemoryModel
    pre_flush.send(SharedMemoryModel, db=db)
    for model in SharedMemoryModel.__subclasses__():
        model.flush_instance_cache(db=db, flush_sub=True)
    post_flush.send(SharedMemoryModel, db=db)
