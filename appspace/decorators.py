from functools import partial, update_wrapper
from stuf.utils import selfname, getter, setter, instance_or_class

from .utils import lazy_import


def delegatable(**kw):
    '''
    marks method as being able to be delegated

    @param **fkw: attributes to set on decorated method
    '''
    def wrapped(func):
        return Delegatable(func, **kw)
    return wrapped


def lazy_component(branch=None):
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

    '''lazily set appspaced component as class attribute on first access'''

    def __init__(self, label, branch=''):
        '''
        init

        @param label: component label
        @param branch: component branch (default: '')
        '''
        self.label = label
        self.branch = branch

    def __get__(self, this, that):
        return self.component(
            self.appspace(this, that), self.label, self.branch
        )

    @staticmethod
    def appspace(this, owner):
        '''
        get the appspace attached to a class

        @param this: an instance
        @param owner: the instance's class
        '''
        appspace = instance_or_class('a', this, owner)
        if appspace is None:
            appspace = this.appspace = lazy_import('appspace.builder.app')
        return appspace

    @staticmethod
    def component(self, appspace, label, branch=None):
        '''
        get component from appspace

        @param appspace: appspace
        @param label: component label
        @param branch: component branch (default: None)
        '''
        return appspace[branch][label] if branch else appspace[label]


class FuncComponent(component):

    def __init__(self, method, branch=None):
        '''
        init

        @param label: component label
        @param branch: component branch (default: None)
        '''
        super(FuncComponent, self).__init__(selfname(method), branch)
        self.method = method
        self.is_set = False
        update_wrapper(self, method)


class Delegatable(FuncComponent):

    delegated = True

    def __get__(self, this, that):
        method = self.method
        delegates = that._delegates
        if delegates:
            kw = dict(
                (k, getter(that, v)) for k, v in delegates.iteritems()
                if hasattr(that, k)
            )
            if kw:
                method = partial(method, **kw)
        return setter(that, self.name, method)


class LazyComponent(FuncComponent):

    '''lazily set appspaced component as class attribute on first access'''

    def __get__(self, this, that):
        aspace = self.appspace(this, that)
        if not self.is_set:
            aspace.set(self.label, self.method(this))
            self.is_set = True
        return self.component(aspace, self.label, self.branch)


class On(FuncComponent):

    '''attach events to method'''

    def __init__(self, method, branch=None, *events):
        '''
        init

        @param method: method to tie to events
        @param *args: events
        '''
        super(On, self).__init__(method, selfname(method), branch)
        self.events = events

    def __get__(self, this, that):
        if not self.is_set:
            ebind = self.appspace(this, that).events.bind
            method = self.method
            for arg in self.events:
                ebind(arg, method)
            self.is_set = True
        return self.method
