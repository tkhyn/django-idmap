"""
Thread local storage for instances cache
"""

import threading
from weakref import WeakValueDictionary
from collections import defaultdict


_tls = threading.local()


def get_cache(cls, reset=False):
    try:
        cls_dict = _tls.idmap_cache
    except AttributeError:
        _tls.idmap_cache = cls_dict = defaultdict(dict)

    # using defaultdict.get does not create the key if it does not exist
    cache = cls_dict.get(cls)
    if not reset and cache is not None:
        return cache

    new_cache_func = dict if cls.use_strong_refs else WeakValueDictionary
    if cls.multi_db:
        cache = defaultdict(new_cache_func)
    else:
        cache = new_cache_func()
    cls_dict[cls] = cache
    return cache


def cache_instance(cls, instance):
    cache = get_cache(cls)
    if cls.multi_db:
        cache[instance._state.db][instance.pk] = instance
    else:
        cache[instance.pk] = instance


def get_cached_instance(cls, pk, db=None):
    cache = get_cache(cls)
    try:
        if cls.multi_db:
            assert db is not None, \
                'A database should be provided to retrieve an instance of a ' \
                'model having multi_db=True'
            return cache[db][pk]
        else:
            return cache[pk]
    except KeyError:
        return None


def flush_cached_instance(cls, instance):
    cache = get_cache(cls)
    try:
        if cls.multi_db:
            del cache[instance._state.db][instance.pk]
        else:
            del cache[instance.pk]
    except KeyError:
        pass
