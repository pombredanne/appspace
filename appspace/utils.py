# -*- coding: utf-8 -*-
'''appspace utilities'''

from __future__ import absolute_import
from functools import wraps
from importlib import import_module
from collections import Mapping, Sequence

from stuf.util import OrderedDict, deleter, getter, lazy


def instance_or_class(key, instance, owner):
    '''
    get attribute of an instance or class

    @param key: name of attribute to look for
    @param instance: instance to check for attribute
    @param owner: class to check for attribute
    '''
    return getter(instance, key, getter(owner, key))


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


def object_lookup(path, this):
    '''
    look up an attribute on an object or its child objects

    @param path: path in object
    @param this: object to lookup on
    '''
    for part in path:
        result = getter(this, part)
        if result is not None:
            this = result
        else:
            return result


def object_walk(this, path=None):
    '''
    look up an attribute on an object and return its paths

    @param this: object to lookup on
    @param path: path in object (default: None)
    '''
    if path is None:
        path = ()
    if isinstance(this, Mapping):
        for key, value in this.iteritems():
            for child in object_walk(value, path + (key,)):
                yield child
    elif isinstance(this, Sequence) and not isinstance(this, basestring):
        for index, value in enumerate(this):
            for child in object_walk(value, path + (index,)):
                yield child
    else:
        yield path, this


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
        instdict = vars(self)
        classdict = self.__class__.__dict__
        desc = self._descriptor_class
        # To reset them, we simply remove them from the instance dict. At that
        # point, it's as if they had never been computed. On the next access,
        # the accessor function from the parent class will be called, simply
        # because that's how the python descriptor protocol works.
        for key, value in classdict.iteritems():
            if key in instdict and isinstance(value, desc):
                deleter(self, key)
