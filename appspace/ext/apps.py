# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002,w0221
'''appspace application extensions'''

from __future__ import absolute_import

from stuf.utils import setter, selfname, lazy

from appspace.managers import Manager
from appspace.error import ConfigurationError
from appspace.builders import Appspace, Patterns, patterns

from .core import Builder
from .settings import Settings
from .events import EventManager
from .keys import AEventManager, ASettings, NoDefault


def on(*events):
    '''
    marks method as being a lazy instance

    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class AppManager(Manager):

    '''state manager'''

    __slots__ = ('_key', '_label', '_settings', 'events', 'settings')

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(AppManager, self).__init__(label, ns)
        self.easy_register(ASettings, 'default', Settings)
        self.easy_register(AEventManager, 'default', EventManager)

    @lazy
    def events(self):
        '''get appspace events manager'''
        return self.easy_lookup(AEventManager, self._settings)(self)

    @lazy
    def settings(self):
        '''get appspace settings'''
        return self.easy_lookup(ASettings, self._settings)()


class AppPatterns(Patterns):

    '''patterns for manager configured by class'''

    _manager = AppManager

    @classmethod
    def settings(cls, appconf, required, defaults):
        '''
        attach settings to class

        @param required: required settings
        @param defaults: default settings
        '''
        conf = appconf.manager.settings
        conf.required = required
        conf.defaults = defaults

    @classmethod
    def build(cls, required=None, defaults=None):
        '''
        build manager configuration from class

        @param required: required settings
        @param defaults: default settings
        '''
        appconf = super(AppPatterns, cls).build()
        if required is not None and defaults is not None:
            cls.settings(appconf, required, defaults)
        return appconf


class AppQuery(Builder):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: appspace or appspace server
        '''
        Builder.__init__(self, appspace, *args, **kw)
        # appspace settings
        self._settings = self._appspace.manager.settings
        self._events = self._appspace.manager.events
        # enable for traits
        self._enable = True

    @property
    def _manage_class(self):
        return Appspace(AppManager())

    @classmethod
    def appspace(cls, pattern, required=None, defaults=None, *args, **kw):
        '''
        build new appspace

        @param pattern: pattern configuration class or appspace label
        @param required: required settings (default: None)
        @param defaults: default settings (default: None)
        @param *args: tuple of module paths or component inclusions
        '''
        # from appspace configuration class...
        if issubclass(pattern, Patterns):
            return cls(pattern.build(required, defaults))
        # from label and arguments...
        elif isinstance(pattern, basestring) and args:
            return cls(AppPatterns.settings(
                patterns(pattern, *args, **kw), required, defaults,
            ))
        raise ConfigurationError('patterns not found')

    def bind(self, event, label, branch=False):
        '''
        bind app to event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.bind(event, self.app(label, branch).first())
        return self

    def burst(self, label, queue):
        '''
        process event subscribers on contents of queue

        @param label: event label
        @param queue: queued arguments
        '''
        self.appendleft(self._events.burst(label, queue))
        return self

    def defaults(self):
        '''default settings by their lonesome'''
        self.appendleft(self._settings.defaults)
        return self

    def event(self, label, priority=False, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: False)
        '''
        # unregister event
        if not priority or not kw:
            self._manager.unregister(label)
            return self
        # register event if priority and keywords passed
        self.appendleft(self._manager.register(label, priority, **kw))
        return self

    def fire(self, event, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param event: event label
        '''
        self.appendleft(self._events.fire(event, *args, **kw))
        return self

    def lock(self):
        '''lock settings so they are read only except locals'''
        self._settings.lock()

    def register(self, model):
        '''
        register model in appspace

        @param model: class to be model
        '''
        # attach manager
        setter(model, 'A', self._appspace)
        # attach manager settings
        setter(model, 'S', self._settings.final)
        self.appendleft(model)
        return self

    def required(self):
        '''required settings by their lonesome'''
        self.appendleft(self._settings.required)
        return self

    def setting(self, label, value=NoDefault, default=None):
        '''
        change setting in application settings

        @param label: setting label
        @param value: value in settings (default: NoDefault)
        @param default: setting value (default: None)
        '''
        if value is not NoDefault:
            self._settings.set(label, value)
            return self
        self.appendleft(self._settings.get(label, default))
        return self

    def trigger(self, label):
        '''
        get objects bound to an event

        @param label: event label
        '''
        return self(self._events.react(label))

    def unbind(self, event, label, branch=False):
        '''
        unbind application from event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.unbind(event, self.app(label, branch).first())
        return self


# shortcut
__ = AppQuery


class On(object):

    '''attach events to method'''

    def __init__(self, method, *metadata):
        self.method = method
        self.metadata = metadata

    def __get__(self, this, that):
        ebind = __(that).manager.events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, selfname(method), method)


__all__ = ('AppManager', 'AppPatterns', 'AppQuery',  '__', 'on')
