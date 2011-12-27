# -*- coding: utf-8 -*-
'''appspace query'''

from __future__ import absolute_import

from collections import deque
from inspect import getmro, ismethod
from functools import partial, update_wrapper

from stuf.utils import OrderedDict, getter, selfname, setter

from appspace.error import NoAppError, ConfigurationError
from .core import AAppspace, ADelegated
from .builders import Appspace, Patterns, Manager, patterns
from .utils import getcls, itermembers, isrelated, lazy_import


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


class Query(deque):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: an appspace
        '''
        self.this = kw.pop('this', None)
        if AAppspace.providedBy(appspace):
            self.appspace = appspace
        elif any([
            ADelegated.providedBy(appspace),
            ADelegated.implementedBy(getcls(appspace)),
        ]):
            self.this = appspace
            self.appspace = appspace.a
        else:
            raise NoAppError('appspace not found')
        deque.__init__(self, args)

    def __call__(self, *args):
        return getcls(self)(self.appspace, *args, **dict(this=self.this))

    def api(self, that):
        combined = OrderedDict()
        for meths in self.filter(that):
            combined.update(meths)
        this = self.this
        branch = self(self.branchset(self.key().one()))
        self.clear()
        for k, v in combined.iteritems():
            branch.appset(k, v.__get__(None, this))
            self.append((k, v))
        return self

    def appget(self, label, branch=''):
        '''
        fetch component from appspace

        @param label: label for appspace
        @param branch: label for branch (default: '')
        '''
        self.clear()
        self.append(
            self.appspace[branch][label] if branch else self.appspace[label]
        )
        return self

    def appset(self, component, label, branch=''):
        '''
        add new component to appspace

        @param component: new component
        @param label: label for branch appspace
        @param branch: branch to add component to (default: '')
        '''
        if branch:
            appspace = self.branchget(branch).root().one()
        else:
            appspace = self.root().one()
        appspace.set(label, component)
        self.clear()
        self.append(component)
        return self

    def branchget(self, branch):
        '''
        fetch branch appspace

        @param branch: label for branch
        '''
        return self.freshen(self.appspace[branch])

    def branchset(self, label):
        '''
        add branch appspace to parent appspace

        @param label: label of new appspace
        '''
        new_appspace = Appspace(Manager())
        self.root().one().set(label, new_appspace)
        return self.freshen(new_appspace)

    @classmethod
    def create(cls, pattern, required, defaults, *args, **kw):
        '''
        build new appspace

        @param pattern: pattern configuration class or name of appspace
        @param required: required settings
        @param defaults: default settings
        @param *args: tuple of module paths or component inclusions
        '''
        if isinstance(patterns, Patterns):
            return cls(pattern.build(required, defaults))
        elif isinstance(pattern, basestring) and args:
            return cls(patterns(pattern, *args, **kw))
        raise ConfigurationError('patterns not found')

    def delegated(self):
        combined = {}
        for meths in self.filter(delegated).one():
            combined.update(self(meths).delegatable.one())
        keys = set()
        for k in combined.iterkeys():
            keys.add(k)
        self.settings().one().delegates[self.key().one()] = keys
        return self

    def delegatable(self):
        self.api(Delegatable)
        return self

    def filter(self, that):
        '''
        filter object members by class

        @param that: class to filter by
        '''
        self.clear()
        self.extend(
            (k, v) for k, v in itermembers(self.this, ismethod)
            if isrelated(v, that)
        )
        return self

    def freshen(self, this):
        self.clear()
        self.append(this)
        return self

    def get(self, key, default=None):
        return self.freshen(self.settings.get(key, default))

    def localize(self, **kw):
        '''generate local settings for component'''
        this = self.this
        local = self.settings().one().local
        key = self.key()
        local_settings = local[key] = dict(
          dict((k, v) for k, v in vars(m).iteritems() if not k.startswith('_'))
          for m in [
              b.Meta for b in getmro(getcls(this)) if hasattr(b, 'Meta')
          ] + [this.Meta]
        )
        local_settings.update(kw)
        return self.freshen(local_settings)

    def key(self):
        '''identifier for component'''
        return self.freshen(
            '_'.join([self.this.__module__, selfname(self.this)])
        )

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
        return self.freshen(appspaced)

    def root(self):
        return self.freshen(self.appspace.appspace)

    def set(self, key, value):
        self.settings.set(key, value)
        return self

    def settings(self):
        return self.freshen(self.appspace.appspace.settings)


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
        return __(that).get(self.label, self.branch)


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
        __(that).appset(self.method(this), self.label, self.branch)
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
        ebind = __(that).root().one().events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, self.label, self.method)


# shortcut
__ = Query
