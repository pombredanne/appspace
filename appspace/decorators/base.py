# -*- coding: utf-8 -*-
'''appspace decorators'''

from functools import partial, update_wrapper
from stuf.utils import selfname, getter, setter

from appspace.query import __


def delegatable(**kw):
    '''
    marks method as being able to be delegated

    @param **kw: delegated attributes to set on decorated method
    '''
    def wrapped(func):
        return Delegatable(func, **kw)
    return wrapped


def lazy_component(branch=''):
    '''
    marks method as being a lazy component

    @param label: component label
    @param branch: component branch (default: None)
    '''
    def wrapped(func):
        return LazyComponent(func, branch)
    return wrapped


def on(*events):
    '''
    marks method as being a lazy component

    @param label: component label
    @param branch: component branch (default: None)
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class component(object):

    '''attach appspaced component directly to class'''

    def __init__(self, label, branch=''):
        '''
        @param label: component label
        @param branch: component branch (default: '')
        '''
        self.label = label
        self.branch = branch
        self._appspace = False

    def __get__(self, this, that):
        return self.calculate(this, that)

    def __set__(self, this, value):
        raise AttributeError('attribute is read only')

    def __delete__(self, this):
        raise AttributeError('attribute is read only')

    def calculate(self, this, that):
        return setter(that, self.label, self.component(this, that))

    def component(self, this, that):
        '''
        get component from appspace

        @param this: an instance
        @param that: the instance's class
        '''
        return __.class_space(self, this, that).get(self.label, self.branch)


class delegated(component):

    '''delegated component'''


class LazyComponent(component):

    '''lazily load appspaced component'''

    def __init__(self, method, branch=''):
        '''
        @param label: component label
        @param branch: component branch (default: '')
        '''
        super(LazyComponent, self).__init__(selfname(method), branch)
        self.method = method
        update_wrapper(self, method)

    def compute(self, this, that):
        __.class_space(self, this, that).app(
            self.label, self.branch, self.method(this)
        )
        return super(LazyComponent, self).compute(this, that)


class Delegatable(LazyComponent):

    '''appspace component that can be delegated to another class'''

    def compute(self, this, that):
        method = self.method
        delegates = that._delegates
        if delegates:
            kw = dict(
                (k, getter(that, v)) for k, v in delegates.iteritems()
                if hasattr(that, k)
            )
            if kw:
                method = partial(method, **kw)
        return setter(that, self.label, method)


class On(LazyComponent):

    '''attach events to method'''

    def __init__(self, method, branch='', *events):
        super(On, self).__init__(method, selfname(method), branch)
        self.events = events

    def compute(self, this, that):
        ebind = __.class_space(self, this, that).events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, self.label, self.method)
