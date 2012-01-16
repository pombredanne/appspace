# -*- coding: utf-8 -*-
'''utilities'''

from __future__ import absolute_import

from inspect import isclass
from functools import wraps
from keyword import iskeyword

from importlib import import_module

from stuf import stuf
from stuf.utils import OrderedDict, getcls, lazybase


def lazy_import(path, attribute=None):
    '''
    deferred module loader

    @param path: something to load
    @param attribute: attribute on loaded module to return
    '''
    if isinstance(path, str):
        try:
            dot = path.rindex('.')
            # import module
            path = getattr(import_module(path[:dot]), path[dot + 1:])
        # If nothing but module name, import the module
        except AttributeError:
            path = import_module(path)
        if attribute:
            path = getattr(path, attribute)
    return path


def lru_cache(max_length=100):
    '''
    least-recently-used cache decorator from Raymond Hettinger

    arguments to the cached function must be hashable.

    @param max_length: maximum number of results in LRU cache (default: 100)
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
                if len(cache) >= max_length:
                    cache.popitem(0)
            # record recent use of this key
            cache[key] = result
            return result
        return wrapper
    return wrapped


def object_walk(this):
    '''
    transform classes within an object into stufs

    @param this: object
    '''
    this_stuf = stuf()
    for k, v in vars(this).iteritems():
        if not k.startswith('_'):
            if isclass(v):
                this_stuf[k] = object_walk(v)
            else:
                this_stuf[k] = v
    return this_stuf


class CheckName(object):

    '''ensures a string is a legal Python name'''

    # Illegal characters for Python names
    ic = '()[]{}@,:`=;+*/%&|^><\'"#\\$?!~'

    def __call__(self, name):
        '''
        ensures a string is a legal python name

        @param name: name to check
        '''
        # Remove characters that are illegal in a Python name
        name = name.strip().lower().replace('-', '_').replace(
            '.', '_'
        ).replace(' ', '_')
        name = ''.join(i for i in name if i not in self.ic)
        # Add _ if value is a Python keyword
        return name + '_' if iskeyword(name) else name


checkname = CheckName()


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

    _descriptor = lazybase

    def reset(self):
        '''reset accessed lazy attributes'''
        instdict = vars(self)
        classdict = vars(getcls(self))
        desc = self._descriptor
        # To reset them, we simply remove them from the instance dict. At that
        # point, it's as if they had never been computed. On the next access,
        # the accessor function from the parent class will be called, simply
        # because that's how the python descriptor protocol works.
        for key, value in classdict.iteritems():
            if all([key in instdict, isinstance(value, desc)]):
                delattr(self, key)


__all__ = (
    'ResetMixin', 'checkname', 'lazy_import', 'lru_cache', 'object_walk',
)
