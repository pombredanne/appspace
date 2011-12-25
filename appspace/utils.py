# -*- coding: utf-8 -*-
'''utilities'''

from __future__ import absolute_import

from inspect import isclass
from types import InstanceType
from importlib import import_module
from functools import update_wrapper, wraps

from stuf import stuf
from stuf.utils import (
    OrderedDict, clsname, getter, instance_or_class, selfname)


def add_article(name):
    '''
    Returns a string containing the correct indefinite article ('a' or 'an')
    prefixed to the specified string.
    '''
    return 'an ' + name if name[:1].lower() in 'aeiou' else 'a ' + name


def class_of(this):
    '''
    Returns a string containing the class name of an object with the correct
    indefinite article ('a' or 'an') preceding it.
    '''
    if isinstance(this, basestring):
        return add_article(this)
    return add_article(clsname(this))


def get_appspace(this, owner):
    '''
    get the appspace attached to a class

    @param this: an instance
    @param owner: the instance's class
    '''
    appspace = instance_or_class('a', this, owner)
    if appspace is None:
        appspace = this.appspace = lazy_import('appspace.builder.app')
    return appspace


def getcls(this):
    '''
    get class

    @param this: object
    '''
    return getter(this, '__class__')


def get_component(appspace, label, branch=None):
    '''
    get component from appspace

    @param appspace: appspace
    @param label: component label
    @param branch: component branch (default: None)
    '''
    return appspace[branch][label] if branch is not None else appspace[label]


def get_members(this, predicate=None):
    '''
    A safe version of inspect.getmembers that handles missing attributes.

    This is useful when there are descriptor based attributes that for some
    reason raise AttributeError even though they exist.  This happens in
    zope.inteface with the __provides__ attribute.
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


class component(object):

    '''lazily set appspaced component as class attribute on first access'''

    def __init__(self, label, branch=None):
        '''
        init

        @param label: component label
        @param branch: component branch (default: None)
        '''
        self.label = label
        self.branch = branch

    def __get__(self, this, that):
        return get_component(get_appspace(this, that), self.label, self.branch)


def lazy_component(branch=None):
    '''
    marks method as being a lazy component

    @param label: component label
    @param branch: component branch (default: None)
    '''
    def wrapped(func):
        return LazyComponent(func, branch)
    return wrapped


class LazyComponent(object):

    '''lazily set appspaced component as class attribute on first access'''

    def __init__(self, method, branch=None):
        '''
        init

        @param label: component label
        @param branch: component branch (default: None)
        '''
        self.method = method
        self.label = selfname(method)
        self.branch = branch
        self.is_set = False
        update_wrapper(self, method)

    def __get__(self, this, that):
        aspace = get_appspace(this, that)
        if not self.is_set:
            aspace.set(self.label, self.method(this))
            self.is_set = True
        return get_component(aspace, self.label, self.branch)
