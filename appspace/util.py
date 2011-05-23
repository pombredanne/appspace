'''appspace utilities'''

from functools import wraps
from collections import OrderedDict

def lru_cache(maxsize=100):
    '''
    Least-recently-used cache decorator.

    From Raymond Hettinger

    Arguments to the cached function must be hashable.

    @param maxsize: maximum number of results in LRU cache
    '''
    def wrapped(func):
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
    return wrapped


class lazy(object):

    '''Lazily assign attributes to instance on first access'''

    def __init__(self, method):
        self.method = method
        try:
            self.__doc__ = method.__doc__
            self.__module__ = method.__module__
            self.__name__ = method.__name__
        except:
            pass

    def __get__(self, instance, cls=None):
        if instance is None: return self
        value = self.method(instance)
        setattr(instance, self.method.__name__, value)
        return value