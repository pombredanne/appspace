# -*- coding: utf-8 -*-
'''appspace query'''

from __future__ import absolute_import

from inspect import getmro, ismethod
from functools import partial, update_wrapper

from stuf.utils import getter, instance_or_class, selfname, setter

from .core import AAppspace, ADelegated
from .builders import Appspace, AppspaceManager, patterns
from .utils import getcls, itermembers, isrelated, lazy_import
from appspace.error import NoAppError


def delegatable(**metadata):
    '''
    marks method as delegatable

    @param **metadata: metadata to set on decorated method
    '''
    def wrapped(func):
        return Delegatable(func, **metadata)
    return wrapped


def lazy_component(branch=''):
    '''
    marks method as a lazily loaded component

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


class AppQuery(list):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: an appspace
        '''
        self.this = kw.pop('this', None)
        if AAppspace.providedBy(appspace):
            self.appspace = appspace
        elif ADelegated.implementedBy(appspace):
            self.this = appspace
            self.appspace = appspace.a
        else:
            raise NoAppError('appspace not found')
        list.__init__(self, args)

    def __call__(self, *args):
        return getcls(self)(self.appspace, *args, **dict(this=self.this))

    def all(self):
        '''fetch all results'''
        return [i for i in self]

    def api(self, that):
        combined = {}
        for meths in self.filter(that).one():
            combined.update(meths)
        this = self.this
        branch = self(self.branchset(self.key().one()))
        for k, v in combined.iteritems():
            branch.appset(k, v.__get__(None, this))
        return self(combined)

    def appget(self, label, branch=''):
        '''
        fetch component from appspace

        @param label: label for appspace
        @param branch: appspace to add component to
        '''
        return self(
            self.appspace[branch][label] if branch else self.appspace[label]
        )

    def appset(self, component, label, branch=''):
        '''
        add new component to appspace

        @param component: new component
        @param label: label for branch appspace
        @param branch: branch to add component to (default: '')
        '''
        self.appspace.appspace.set(label, component)
        return self

    def branchget(self, desc, that):
        '''
        fetch appspace attached to class

        @param desc: an instance
        @param that: the instance's class
        '''
        this = self.this
        if not desc.appspace:
            appspace = instance_or_class('a', this, that)
            if appspace is None:
                appspace = this.a = lazy_import('appspace.builder.app')
            desc.appspace = appspace
        return self

    def branchset(self, label):
        '''
        add branch appspace to parent appspace

        @param label: label of new appspace
        '''
        appspace = self.appspace
        if label not in appspace:
            new_appspace = Appspace(AppspaceManager())
            appspace.appspace.set(label, new_appspace)
        return self

    def build(self, pattern_class, required, defaults):
        '''
        build new appspace

        @param pattern_class: pattern configuration class
        @param required: required settings
        @param defaults: default settings
        '''
        return getcls(self)(pattern_class.build(required, defaults))

    def delegated(self):
        combined = {}
        for meths in self.filter(delegated).one():
            combined.update(self(meths).delegatable.one())
        keys = set()
        for k in combined.iterkeys():
            keys.add(k)
        self.appspace.appspace.settings.delegates[self.key().one()] = keys
        return self

    def delegatable(self):
        return self(self.api(Delegatable))

    def filter(self, that):
        '''
        filter object members by class

        @param that: class to filter by
        '''
        return self(
            *tuple((k, v) for k, v in itermembers(self.this, ismethod)
            if isrelated(v, that))
        )

    def load(self, label, *args, **kw):
        '''
        configuration for branch appspace

        @param label: name of branch appspace
        @param *args: tuple of module paths or component inclusions
        '''
        return self(patterns(label, *args, **kw))

    def localize(self, **kw):
        '''generate local settings for component'''
        this = self.this
        local = self.appspace.appspace.settings.local
        key = self.key()
        local_settings = local[key] = dict(
          dict((k, v) for k, v in vars(m).iteritems() if not k.startswith('_'))
          for m in [
              b.Meta for b in getmro(getcls(this)) if hasattr(b, 'Meta')
          ] + [this.Meta]
        )
        local_settings.update(kw)
        return self(local_settings)

    def key(self):
        '''identifier for component'''
        this = self.this
        return self('_'.join([this.__module__, selfname(this)]))

    def one(self):
        '''fetch one result'''
        try:
            return self[0]
        except IndexError:
            return []

    def ons(self):
        return self.api(On)

    first = one

    def register(self, appspaced):
        '''
        add appspace to appspaced class

        @param appspaced: class to add appspace to
        '''
        # attach appspace
        setter(appspaced, 'a', self.appspace)
        # attach appspace settings
        setter(appspaced, 's', self.appspace.appspace.settings)
        return self


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


# shortcut
__ = AppQuery
