# -*- coding: utf-8 -*-
'''appspace extension utilities'''

from __future__ import absolute_import

from functools import partial, update_wrapper

from stuf.utils import getter, selfname, setter

from .query import __
from appspace.core import ADelegatable, ADelegated, appifies


def delegatable(*metadata):
    '''
    marks method as delegatable

    @param *metadata: metadata to set on decorated method
    '''
    def wrapped(func):
        return Delegatable(func, *metadata)
    return wrapped


def lazy_component(branch=''):
    '''
    marks method as a lazily loaded component

    @param branch: component branch (default: '')
    '''
    def wrapped(func):
        return LazyComponent(func, branch)
    return wrapped


def on(*events):
    '''
    marks method as being a lazy component

    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class component(object):

    '''attach appspaced component to class'''

    def __init__(self, label, branch=''):
        '''
        @param label: component label
        @param branch: component branch (default: '')
        '''
        self.label = label
        self.branch = branch
        self._appspace = False

    def __get__(self, this, that):
        return self.calculate(that)

    def __set__(self, this, value):
        raise AttributeError('attribute is read only')

    def __delete__(self, this):
        raise AttributeError('attribute is read only')

    def __repr__(self, *args, **kwargs):
        return '{label}@{branch}'.format(label=self.label, branch=self.branch)

    def calculate(self, that):
        return self.component(that)

    def component(self, that):
        '''
        get component from manager

        @param that: the instance's class
        '''
        return __(that).app(self.label, self.branch).one()


class delegated(component):

    '''delegated component'''

    appifies(ADelegated)


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

    def build(self, this, that):
        __(that).app(self.label, self.branch, self.method(this))
        return super(LazyComponent, self).build(this, that)


class Delegatable(LazyComponent):

    '''manager component that can be delegated to another class'''

    appifies(ADelegatable)

    def __init__(self, method, branch='', *metadata):
        super(Delegatable, self).__init__(method, branch)
        self.metadata = metadata

    def build(self, this, that):
        method = self.method
        if self.metadata:
            kw = dict(
                (k, getter(that, k)) for k in self.metadata if hasattr(that, k)
            )
            if kw:
                method = partial(method, **kw)
        return setter(that, self.label, method)


class On(LazyComponent):

    '''attach events to method'''

    def __init__(self, method, branch='', *events):
        super(On, self).__init__(method, branch)
        self.events = events

    def build(self, this, that):
        ebind = __(that).manager.events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, self.label, self.method)
