'''appspace utilities'''

from functools import wraps
from collections import OrderedDict

def lru_cache(maxsize=100):
    '''Least-recently-used cache decorator.

    From Raymond Hettinger

    Arguments to the cached function must be hashable.

    @param maxsize: maximum number of results in LRU cache
    '''
    def decorating_function(func):
        # order: least recent to most recent
        cache = OrderedDict()
        @wraps(func)
        def wrapper(*args, **kw):
            key = args
            if kw: key += tuple(sorted(kw.items()))
            try:
                result = cache.pop(key)
            except KeyError:
                result = func(*args, **kw)
                # purge least recently used cache entry
                if len(cache) >= maxsize: cache.popitem(0)
            # record recent use of this key
            cache[key] = result
            return result
        return wrapper
    return decorating_function


class reify(object):

    '''Put the result of a method which uses this (non-data) descriptor
    decorator in the instance dict after the first call, effectively replacing
    the decorator with an instance variable.

    From pyramid by Agendaless Consulting
    '''

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None: return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val