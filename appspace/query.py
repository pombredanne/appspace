# -*- coding: utf-8 -*-
'''manager query'''

from __future__ import absolute_import

from collections import deque
from inspect import getmro, ismethod
from functools import partial, update_wrapper

from stuf.utils import OrderedDict, getter, selfname, setter

from .core import AAppspace, ADelegated
from .utils import getcls, isrelated, itermembers
from .error import NoAppError, ConfigurationError
from .builders import Appspace, Manager, Patterns, patterns


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

    @param branch: component branch (default: None)
    '''
    def wrapped(func):
        return LazyComponent(func, branch)
    return wrapped


def on(*events):
    '''
    marks method as being a lazy component

    @param label: component label
    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class Query(deque):

    '''manager query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param manager: an manager
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

    def _freshen(self, this):
        '''
        clear and put one thing in queue

        @param this: the thing
        '''
        # clear
        self.clear()
        # append to queue
        self.append(this)
        return self

    def api(self, that):
        '''
        fetch api matching type of class

        @param that: class to filter by
        '''
        combined = OrderedDict()
        for meths in self.filter(that):
            combined.update(meths)
        this = self.this
        branch = self(self.branch(self.key().one()))
        self.clear()
        for k, v in combined.iteritems():
            branch.app(k, v.__get__(None, this))
            self.append((k, v))
        return self

    def app(self, label, branch='', component=''):
        '''
        add or get app from appspace

        @param label: app label
        @param branch: branch label (default: '')
        @param component: new component (default: '')
        '''
        try:
            if branch:
                return self.appspace[branch][label]
            return self.appspace[label]
        except NoAppError:
            if component:
                if branch:
                    manager = self.branch(branch).one().manager
                else:
                    manager = self.appspace.manager
                manager.set(label, component)
                return self._freshen(component)
        raise ConfigurationError('invalid application')

    def branch(self, label):
        '''
        add or get branch appspace

        @param label: label of new appspace
        '''
        try:
            return self._freshen(self.appspace[label])
        except NoAppError:
            new_appspace = Appspace(Manager())
            self.appspace.manager.set(label, new_appspace)
            return self._freshen(new_appspace)

    @classmethod
    def create(cls, pattern, required, defaults, *args, **kw):
        '''
        build new appspace

        @param pattern: pattern configuration class or label of appspace
        @param required: required settings
        @param defaults: default settings
        @param *args: tuple of module paths or component inclusions
        '''
        if isinstance(patterns, Patterns):
            return cls(pattern.build(required, defaults))
        elif isinstance(pattern, basestring) and args:
            appconf = patterns(pattern, *args, **kw)
            return cls(Patterns.settings(appconf, required, defaults))
        raise ConfigurationError('patterns not found')

    def delegated(self):
        '''list delegated attributes'''
        combined = {}
        for meths in self.filter(delegated).one():
            combined.update(self(meths).delegatable.one())
        keys = set()
        for k in combined.iterkeys():
            keys.add(k)
        self.appspace.manager.settings.delegates[self.key().one()] = keys
        return self

    def delegatable(self):
        '''list delegatable attributes'''
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

    def get(self, key, default=None):
        '''
        get a setting's value

        @param key: setting key
        @param default: setting value (default: None)
        '''
        return self._freshen(self.settings.get(key, default))

    def localize(self, **kw):
        '''
        generate local settings for component

        **kw: settings to add to local settings
        '''
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
        return self._freshen(local_settings)

    def key(self):
        '''identifier for component'''
        return self._freshen(
            '_'.join([self.this.__module__, selfname(self.this)])
        )

    def manager(self):
        '''fetch appspace manager'''
        return self._freshen(self.appspace.manager)

    def one(self):
        '''fetch one result'''
        try:
            return self[0]
        except IndexError:
            return []

    def ons(self):
        '''list of events'''
        return self.api(On)

    first = one

    def register(self, appspaced):
        '''
        add appspace to class

        @param appspaced: class to be appspaced
        '''
        # attach manager
        setter(appspaced, 'a', self.appspace)
        # attach manager settings
        setter(appspaced, 's', self.appspace.manager.settings)
        return self._freshen(appspaced)

    def set(self, key, value):
        '''
        change setting in application settings

        @param key: name of settings
        @param value: value in settings
        '''
        self.appspace.manager.settings.set(key, value)
        return self

    def settings(self):
        '''appspace settings'''
        return self._freshen(self.appspace.manager.settings)


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
        get component from manager

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
        __(that).app(self.label, self.branch, self.method(this))
        return super(LazyComponent, self).compute(this, that)


class Delegatable(LazyComponent):

    '''manager component that can be delegated to another class'''

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
        ebind = __(that).manager().one().events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, self.label, self.method)


# shortcut
__ = Query
