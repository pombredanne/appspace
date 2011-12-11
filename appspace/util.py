# -*- coding: utf-8 -*-
## pylint: disable-msg=w0702
'''appspace utilities'''

from functools import wraps
from importlib import import_module
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
    
def deferred_import(module_path, attribute=None):
    '''
    deferred module loader

    @param module_path: something to load
    @param attribute: attributed on loaded module to return 
    '''
    if isinstance(module_path, str):
        try:
            dot = module_path.rindex('.')
            # import module
            module_path = getattr(
                import_module(module_path[:dot]), module_path[dot+1:]
            )
        # If nothing but module name, import the module
        except AttributeError:
            module_path = import_module(module_path)
        if attribute:
            module_path = getattr(module_path, attribute)
    return module_path

def lru_cache(maxsize=100):
    '''
    least-recently-used cache decorator from Raymond Hettinger

    arguments to the cached function must be hashable.

    @param maxsize: maximum number of results in LRU cache (default: 100)
    '''
    def wrapped(func):
        # order: least recent to most recent
        cache = OrderedDict()
        @wraps(func)
        def wrapper(*args, **kw):
            key = args
            if kw: 
                key += tuple(sorted(kw.items()))
            try:
                result = cache.pop(key)
            except KeyError:
                result = func(*args, **kw)
                # purge least recently used cache entry
                if len(cache) >= maxsize: 
                    cache.popitem(0)
            # record recent use of this key
            cache[key] = result
            return result
        return wrapper
    return wrapped


class lazy_base(object):

    '''lazy base class'''

    def __init__(self, method):
        self.method = method
        try:
            self.__doc__ = method.__doc__
            self.__module__ = method.__module__
            self.__name__ = method.__name__
        except:
            pass


class lazy(lazy_base):

    '''lazily assign attributes on an instance on first access'''

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.__dict__[self.__name__] = self.method(instance)
        return value
    
    
class lazy_class(lazy_base):

    '''lazily assign attributes on a class on first use'''

    def __get__(self, instance, owner):
        value = self.method(owner)
        setattr(owner, self.__name__, value) 
        return value
    
    
class ResetMixin(object):

    '''
    mixin class to add a .reset() method to users of "lazy"
    
    By default, auto attributes once computed, become static. If they happen to
    depend on other parts of an object and those parts change, their values may
    now be invalid.

    This class offers a .reset() method that users can call *explicitly* when
    they know the state of their objects may have changed and they want to
    ensure that *all* their special attributes should be invalidated. Once
    reset() is called, all their auto attributes are reset to their lazy 
    descriptors, and their accessor functions will be triggered again.
    '''

    def reset(self):
        '''Reset all OneTimeProperty attributes that may have fired already.'''
        instdict = self.__dict__
        classdict = self.__class__.__dict__
        # To reset them, we simply remove them from the instance dict.    At that
        # point, it's as if they had never been computed.    On the next access,
        # the accessor function from the parent class will be called, simply
        # because that's how the python descriptor protocol works.
        for mname, mval in classdict.items():
            if mname in instdict and isinstance(mval, lazy):
                delattr(self, mname)
