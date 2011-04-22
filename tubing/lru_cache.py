from functools import wraps
from collections import OrderedDict

def lru_cache(maxsize=100):
    '''Least-recently-used cache decorator.

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used
    '''
    def decorating_function(func):
        cache = OrderedDict()   # order: least recent to most recent
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
            cache[key] = result         # record recent use of this key
            return result
        return wrapper
    return decorating_function