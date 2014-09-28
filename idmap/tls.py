"""
Thread local storage for instances cache
"""

import threading
from weakref import WeakValueDictionary


_tls = threading.local()


def init_idmap():
    _tls.idmap_cache = {}


def create_cache(cls, reset=False):
    idm_cache = getattr(_tls, 'idmap_cache', None)
    if not idm_cache:
        # create idmap cache
        init_idmap()
    elif not reset and cls in idm_cache:
        # the class exists in the cache, nothing to do
        return idm_cache[cls]
    new_cache = {} if getattr(cls._meta, 'use_strong_refs', False) \
                else WeakValueDictionary()
    _tls.idmap_cache[cls] = new_cache
    return new_cache


def cache_instance(cls, instance, pk):
    cache = create_cache(cls)
    cache[pk] = instance


def get_cached_instance(cls, pk):
    if not hasattr(_tls, 'idmap_cache'):
        return None
    cache = _tls.idmap_cache.get(cls, None)
    if not cache:
        return None
    return cache.get(pk, None)


def flush_cache_key(cls, pk):
    del _tls.idmap_cache[cls][pk]
