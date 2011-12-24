# -*- coding: utf-8 -*-
'''appspace utilities'''

from __future__ import absolute_import

from functools import wraps
from inspect import isclass
from operator import getitem
from collections import deque
from types import InstanceType
from importlib import import_module

from stuf import stuf
from stuf.utils import OrderedDict, clsname, deleter, getter, lazybase


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


def get_members(this, predicate=None):
    '''
    A safe version of inspect.getmembers that handles missing attributes.

    This is useful when there are descriptor based attributes that for some
    reason raise AttributeError even though they exist.  This happens in
    zope.inteface with the __provides__ attribute.
    '''
    results = []
    for key in dir(this):
        try:
            value = getattr(this, key)
        except AttributeError:
            pass
        else:
            if not predicate or predicate(value):
                results.append((key, value))
    results.sort()
    return results


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


def parse_notifier_name(name):
    '''
    convert the name argument to a list of names.

    Examples
    --------

    >>> parse_notifier_name('a')
    ['a']
    >>> parse_notifier_name(['a','b'])
    ['a', 'b']
    >>> parse_notifier_name(None)
    ['anytrait']
    '''
    if isinstance(name, str):
        return [name]
    elif name is None:
        return ['anytrait']
    elif isinstance(name, (list, tuple)):
        for n in name:
            assert isinstance(n, str), 'names must be strings'
        return name


def repr_type(this):
    '''
    return a string representation of a value and its type for readable error
    messages

    @param this: value to probe
    '''
    the_type = type(this)
    if the_type is InstanceType:
        # Old-style class.
        the_type = this.__class__
    return '%r %r' % (this, the_type)


def tern(condition, first, second):
    '''
    ternary shortcut

    @param condition: condition that must be true for first choice
    @param first: first expression to return if condition is true
    @param second: second expression to return if condition is false
    '''
    return first if condition else second


class NamedQueue(object):

    '''named queue'''

    __slots__ = ['_queue', 'max_length']

    def __init__(self, max_length=None):
        self._queue = deque(max_length) if max_length is not None else deque()
        self.max_length = max_length

    def __getitem__(self, key):
        for k, v in self:
            if k == key:
                return v
        else:
            raise KeyError('{key} not found'.format(key=key))

    def __iter__(self):
        for k, v in self._queue:
            yield [k, v]

    def __len__(self):
        return len(self._queue)

    def add_args_left(self, key, *args, **kw):
        '''
        add arguments to left side of queue

        @param key: key in queue
        '''
        self._queue.appendleft([key, (args, kw)])

    def add_args_right(self, key, *args, **kw):
        '''
        add arguments to right side of queue

        @param key: key in queue
        '''
        self._queue.append([key, (args, kw)])

    def add_left(self, key, value):
        '''
        dd item to left side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self._queue.appendleft([key, value])

    def add_right(self, key, value):
        '''
        add item to right side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self._queue.append([key, value])

    def clear(self):
        '''clear queue'''
        self._queue.clear()

    def get_left(self, key, default=None):
        '''
        get item by key from left side of queue

        @param key: key in queue
        @param default: default value (default: None)
        '''
        try:
            return getitem(self, key)
        except KeyError:
            return default

    def get_right(self, key, default=None):
        '''
        get item from right side of queue

        @param key: key in queue
        @param default: default vaue (default: None)
        '''
        self.reverse()
        try:
            value = getitem(self, key)
        except KeyError:
            value = default
        self.reverse()
        return value

    def pop_left(self):
        '''pop leftmost item in queue'''
        return self._queue.popleft()

    def pop_right(self):
        '''pop leftmost item in queue'''
        return self._queue.pop()

    def remove_left(self, key):
        '''
        remove item from left side of queue

        @param key: key in queue
        '''
        value = getitem(self, key)
        self._queue.remove(value)

    def remove_right(self, key):
        '''
        remove item from right side of queue

        @param key: key in queue
        '''
        self.reverse()
        value = getitem(self, key)
        self._queue.remove(value)
        self.reverse()

    def reverse(self):
        '''reverse queue order'''
        self._queue.reverse()

    def update_left(self, key, value):
        '''
        get item by key from left side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        for k in self._queue:
            if k[0] == key:
                key[1] = value
        else:
            raise KeyError('{key} not found'.format(key=key))

    def update_right(self, key, value):
        '''
        get item from right side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self.reverse()
        for k in self._queue:
            if k[0] == key:
                key[1] = value
        else:
            self.reverse()
            raise KeyError('{key} not found'.format(key=key))
        self.reverse()


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
