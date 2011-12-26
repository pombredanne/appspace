# -*- coding: utf-8 -*-
'''decorators'''

from functools import partial, update_wrapper
from stuf.utils import selfname, getter, setter, instance_or_class

from appspace.utils import lazy_import, filter_members


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

    def appspace(self, this, that):
        '''
        get appspace attached to class

        @param this: an instance
        @param that: the instance's class
        '''
        if not self._appspace:
            appspace = instance_or_class('a', this, that)
            if appspace is None:
                appspace = this.a = lazy_import('appspace.builder.app')
            self._appspace = appspace
        return self._appspace

    def calculate(self, this, that):
        return setter(that, self.label, self.component(this, that))

    def component(self, this, that):
        '''
        get component from appspace

        @param this: an instance
        @param that: the instance's class
        '''
        appspace = self.appspace(this, that)
        branch = self.branch
        label = self.label
        return appspace[branch][label] if branch else appspace[label]


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
        self.appspace(this, that).set(self.label, self.method(this))
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
        ebind = self.appspace(this, that).events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, self.label, self.method)


# filter out component descriptors
filter_component = partial(filter_members, that=component)
# filter out delegatable descriptors
filter_delegatable = partial(filter_members, that=Delegatable)
# filter out delegated descriptors
filter_delegated = partial(filter_members, that=delegated)
# filter out lazy component descriptors
filter_lc = partial(filter_members, that=LazyComponent)
# filter out event descriptors
filter_on = partial(filter_members, that=On)
