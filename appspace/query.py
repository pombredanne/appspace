# -*- coding: utf-8 -*-
'''appspace query'''

from __future__ import absolute_import

from inspect import getmro, ismethod
from functools import partial, update_wrapper

from stuf import stuf
from stuf.utils import getter, instance_or_class, selfname, setter

from .core import AAppQuery, AAppspace, ADelegated, appifies
from .utils import getcls, itermembers, isrelated, lazy_import
from .builders import Appspace, AppspaceManager, patterns, app


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


class AppQuery(list):

    '''appspace query'''

    appifies(AAppQuery)

    def __init__(self, appspace, *args):
        '''
        @param appspace: an appspace
        '''
        self.this = None
        if AAppspace.providedBy(appspace):
            self.appspace = appspace
        elif ADelegated.providedBy(appspace):
            self.this = appspace
            self.appspace = appspace.a
        list.__init__(self, args)

    def __call__(self, *args):
        '''
        @param appspace: an appspace
        '''
        return getcls(self)(self.appspace, *args)

    def all(self):
        '''fetch all results'''
        return [i for i in self]

    def app(self, label, component, branch='', use_global=False):
        '''
        add new component to appspace

        @param label: label for branch appspace
        @param component: new component
        @param branch: branch to add component to
        @param use_global: use global appspace (default: False)
        '''
        appspace = self.appspace
        if use_global:
            appspace = app
        elif branch:
            appspace = self.add_branch(branch)
        appspace.appspace.set(label, component)
        return self

    def branch(self, label, use_global=False):
        '''
        add new appspace to existing appspace

        @param label: label of new appspace
        @param use_global: use global appspace (default: False)
        '''
        appspace = self.appspace
        if label not in appspace and not use_global:
            new_appspace = Appspace(AppspaceManager())
            appspace.appspace.set(label, new_appspace)
            return new_appspace
        return self

    def build(self, pattern_class, required, defaults):
        '''
        build new appspace

        @param required: required settings
        @param defaults: default settings
        '''
        return self(pattern_class.build(required, defaults))

    def space(self, desc, that):
        '''
        get appspace attached to class

        @param this: an instance
        @param that: the instance's class
        '''
        this = self.this
        if not desc._appspace:
            appspace = instance_or_class('a', this, that)
            if appspace is None:
                appspace = this.a = lazy_import('appspace.builder.app')
            desc._appspace = appspace
        return self(desc._appspace)

    def api(self, that):
        this = self.this
        combined = {}
        for meths in self.filter(this, that):
            combined.update(meths)
        key = self.id(this)
        branch = self(self.branch(key))
        keys = set()
        for k, v in combined.iteritems():
            keys.add(k)
            branch.app(k, v.__get__(None, this))
        self.appspace.settings.delegates[key] = keys
        return self

    def delegateds(self):
        this = self.this
        combined = {}
        for meths in self.filter(this, delegated):
            combined.update(meths)
        key = self.id(this)
        branch = self(self.branch(key))
        keys = set()
        for k, v in combined.iteritems():
            keys.add(k)
            branch.app(k, v.__get__(None, this))
        self.appspace.settings.delegates[key] = keys
        return self

    def delegatables(self):
        this = self.this
        combined = {}
        for meths in self.filter(this, Delegatable):
            combined.update(meths)
        key = self.id(this)
        branch = self(self.branch(key))
        keys = set()
        for k, v in combined.iteritems():
            keys.add(k)
            branch.app(k, v.__get__(None, this))
        self.appspace.settings.delegates[key] = keys
        return self

    def filter(self, that):
        '''
        filter members of an object by class

        @param that: a class
        '''
        this = self.this
        return stuf(
            (k, v) for k, v in itermembers(this, ismethod)
            if isrelated(v, that)
        )

    def get(self, label, branch=''):
        '''
        get component from appspace

        @param label: label for branch appspace
        @param branch: branch to add component to
        '''
        return self(
            self.appspace[branch][label] if branch else self.appspace[label]
        )

    def load(self, label, *args, **kw):
        '''
        configuration for branch appspace

        @param label: name of branch appspace
        @param *args: tuple of module paths or component inclusions
        '''
        return self(patterns(label, *args, **kw))

    def localize(self, this):
        '''
        add local settings to appspace settings

        @param this: an instance
        '''
        local = self.appspace.s.local
        lid = self.id(this)
        local[lid] = dict(
          dict((k, v) for k, v in vars(m).iteritems() if not k.startswith('_'))
          for m in [
              b.Meta for b in getmro(getcls(this)) if hasattr(b, 'Meta')
          ] + [this.Meta]
        )
        return self(self.appspace, local[lid])

    def id(self, this):
        return self(self.appspace, '_'.join([this.__module__, this(self)]))

    def one(self):
        '''fetch one result'''
        return self[0]

    first = one

    def register(self, klass):
        '''
        add appspace to class

        @param appspace: appspace to add
        '''
        setter(klass, 'a', self.appspace)
        setter(klass, 's', self.appspace.settings)
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
