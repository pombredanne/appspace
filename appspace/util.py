# -*- coding: utf-8 -*-
## pylint: disable-msg=w0702
'''appspace utilities'''

from __future__ import absolute_import
from importlib import import_module
from functools import wraps, update_wrapper
from collections import Sequence, Mapping
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
    def wrapped(this):
        # order: least recent to most recent
        cache = OrderedDict()
        @wraps(this)
        def wrapper(*args, **kw):
            key = args
            if kw: 
                key += tuple(sorted(kw.items()))
            try:
                result = cache.pop(key)
            except KeyError:
                result = this(*args, **kw)
                # purge least recently used cache entry
                if len(cache) >= maxsize: 
                    cache.popitem(0)
            # record recent use of this key
            cache[key] = result
            return result
        return wrapper
    return wrapped

def class_name(this):
    '''
    get class name
    
    @param this: object
    '''
    return this.__class__.__name__

def object_name(this):
    '''
    get object name
    
    @param this: object
    '''
    return this.__name__

def object_walk(obj, path=()):
    if isinstance(obj, Mapping):
        for key, value in obj.iteritems():
            for child in object_walk(value, path + (key,)):
                yield child
    elif isinstance(obj, Sequence) and not isinstance(obj, basestring):
        for index, value in enumerate(obj):
            for child in object_walk(value, path + (index,)):
                yield child
    else:
        yield path, obj


class lazy_base(object):

    '''lazy base'''

    def __init__(self, method):
        self.method = method
        try:
            self.__doc__ = method.__doc__
            self.__module__ = method.__module__
            self.__name__ = object_name(method)
        except:
            pass


class lazy(lazy_base):

    '''lazily assign attributes on an instance on first access'''

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.method(instance)
        setattr(instance, self.__name__, value)
        return value
    
class both(lazy):

    '''
    decorator which allows definition of a Python descriptor with both 
    instance-level and class-level behavior
    '''

    def __init__(self, method, expr=None):
        super(both, self).__init__(method)
        self.expr = expr
        update_wrapper(self, method)

    def __get__(self, instance, owner):
        if instance is None:
            return self.expr(owner)
        return super(both, self).__get__(instance, owner)

    def expression(self, expr):
        '''
        a modifying decorator that defines a general method
        '''
        self.expr = expr
        return self
    
    
class lazy_class(lazy_base):

    '''lazily assign attributes on a class on first use'''

    def __get__(self, instance, owner):
        value = self.method(owner)
        setattr(owner, self.__name__, value) 
        return value
    
    
class ResetMixin(object):

    '''
    mixin to add a ".reset()" method to methods decorated with "lazy"
    
    By default, lazy attributes, once computed, are static. If they happen to
    depend on other parts of an object and those parts change, their values may
    be out of sync.

    This class offers a ".reset()" method that an instance can call its state 
    has changed and invalidate all their lazy attributes. Once reset() is 
    called, all lazy attributes are reset to original format and their accessor 
    functions can be triggered again.
    '''
    
    _descriptor_class = lazy

    def reset(self):
        '''reset accessed lazy attributes'''
        instdict = self.__dict__
        classdict = self.__class__.__dict__
        desc = self._descriptor_class
        # To reset them, we simply remove them from the instance dict.    At that
        # point, it's as if they had never been computed.    On the next access,
        # the accessor function from the parent class will be called, simply
        # because that's how the python descriptor protocol works.
        for key, value in classdict.iteritems():
            if key in instdict and isinstance(value, desc):
                delattr(self, key)
