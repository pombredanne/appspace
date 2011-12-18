# -*- coding: utf-8 -*-
'''appspace utilities'''

from __future__ import absolute_import
from functools import wraps
from inspect import isclass
from importlib import import_module

from stuf.utils import OrderedDict, deleter, getter, lazybase


def lazy_import(module_path, attribute=None):
    '''
    deferred module loader

    @param module_path: something to load
    @param attribute: attributed on loaded module to return
    '''
    if isinstance(module_path, str):
        try:
            dot = module_path.rindex('.')
            # import module
            module_path = getter(
                import_module(module_path[:dot]), module_path[dot + 1:]
            )
        # If nothing but module name, import the module
        except AttributeError:
            module_path = import_module(module_path)
        if attribute:
            module_path = getter(module_path, attribute)
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


def object_walk(this):
    '''
    transform classes within an object to a dictionary

    @param this: object
    '''
    this_dict = dict()
    for k, v in vars(this).iteritems():
        if not k.startswith('__'):
            if isclass(v):
                this_dict[k] = object_walk(v)
            else:
                this_dict[k] = v
    return this_dict


class ResetMixin(object):

    '''
    mixin to add a ".reset()" method to methods decorated with "lazybase"

    By default, lazy attributes, once computed, are static. If they happen to
    depend on other parts of an object and those parts change, their values may
    be out of sync.

    This class offers a ".reset()" method that an instance can call its state
    has changed and invalidate all their lazy attributes. Once reset() is
    called, all lazy attributes are reset to original format and their accessor
    functions can be triggered again.
    '''

    _descriptor_class = lazybase

    def reset(self):
        '''reset accessed lazy attributes'''
        instdict = vars(self)
        classdict = vars(self.__class__)
        desc = self._descriptor_class
        # To reset them, we simply remove them from the instance dict. At that
        # point, it's as if they had never been computed. On the next access,
        # the accessor function from the parent class will be called, simply
        # because that's how the python descriptor protocol works.
        for key, value in classdict.iteritems():
            if all([key in instdict, isinstance(value, desc)]):
                deleter(self, key)
