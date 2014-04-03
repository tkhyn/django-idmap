from version import __version__, __version_info__

import warnings

import threading

_tls = threading.local()

def lazy_object(location):
    def inner(*args, **kwargs):
        parts = location.rsplit('.', 1)
        warnings.warn('`idmapper.%s` is deprecated. Please use `%s` instead.' % (parts[1], location), DeprecationWarning)
        imp = __import__(parts[0], globals(), locals(), [parts[1]], -1)
        func = getattr(imp, parts[1])
        if callable(func):
            return func(*args, **kwargs)
        return func
    return inner

SharedMemoryModel = lazy_object('idmapper.models.SharedMemoryModel')

def flush_cache():
    _tls.idmapper_cache = {}
