# -*- coding: utf-8 -*-
'''utilities'''

from __future__ import absolute_import

from functools import wraps
from types import InstanceType
from importlib import import_module
from inspect import isclass, ismethod

from stuf import stuf
from stuf.utils import OrderedDict, clsname, getter


def add_article(name):
    '''
    get string containing the correct indefinite article ('a' or 'an') prefixed
    to the specified string
    '''
    return 'an ' + name if name[:1].lower() in 'aeiou' else 'a ' + name


def class_of(this):
    '''
    get string containing class name of object with the correct indefinite
    article ('a' or 'an') preceding it
    '''
    if isinstance(this, basestring):
        return add_article(this)
    return add_article(clsname(this))


def getcls(this):
    '''
    get class of instance

    @param this: an instance
    '''
    return getter(this, '__class__')


def get_members(this, predicate=None):
    '''
    version of inspect.getmembers that handles missing attributes.

    This is useful when there are descriptor based attributes that for some
    reason raise AttributeError even though they exist.
    '''
    results = []
    rappend = results.append
    for key in dir(this):
        try:
            value = getter(this, key)
        except AttributeError:
            pass
        else:
            if not predicate or predicate(value):
                rappend((key, value))
    results.sort()
    return results


def filter_members(this, that):
    '''
    filter members of an object by class

    @param this: an instance
    @param that: a class
    '''
    return stuf(
        (k, v) for k, v in itermembers(this, ismethod) if isrelated(v, that)
    )


def isrelated(this, that):
    '''
    tell if this object is an instance or subclass of that object

    @param this: an instance
    @param that: a class
    '''
    return issubclass(this, that) if isclass(this) else isinstance(this, that)


def itermembers(that, predicate=None):
    '''
    iterate object members

    @param this: an object
    @param predicate: filter for members (default: None)
    '''
    for key in dir(that):
        try:
            value = getter(that, key)
        except AttributeError:
            pass
        else:
            if not predicate or predicate(value):
                yield key, value


def lazy_import(path, attribute=None):
    '''
    deferred module loader

    @param path: something to load
    @param attribute: attributed on loaded module to return
    '''
    if isinstance(path, str):
        try:
            dot = path.rindex('.')
            # import module
            path = getter(import_module(path[:dot]), path[dot + 1:])
        # If nothing but module name, import the module
        except AttributeError:
            path = import_module(path)
        if attribute:
            path = getter(path, attribute)
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
    transform classes within an object to a dictionary

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


def repr_type(this):
    '''
    return a string representation of a value and its type for readable error
    messages

    @param this: value to probe
    '''
    the_type = type(this)
    if the_type is InstanceType:
        # Old-style class.
        the_type = getcls(this)
    return '%r %r' % (this, the_type)
