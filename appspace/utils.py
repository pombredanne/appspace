# -*- coding: utf-8 -*-
'''utilities'''

from __future__ import absolute_import

from functools import wraps
from keyword import iskeyword

from importlib import import_module

from stuf.utils import OrderedDict


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
__all__ = ('checkname', 'lazy_import', 'lru_cache', 'object_walk')
