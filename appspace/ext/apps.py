# -*- coding: utf-8 -*-
'''appspace extension application query'''

from __future__ import absolute_import

from inspect import getmro

from stuf import stuf
from stuf.utils import get_or_default, setter, selfname

from appspace.utils import getcls
from appspace.managers import Manager
from appspace.error import ConfigurationError
from appspace.builders import Appspace, Patterns, patterns

from .core import Query
from .keys import NoDefaultSpecified

__all__ = ['AppQuery', '__']


def on(*events):
    '''
    marks method as being a lazy instance

    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class AppQuery(Query):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: appspace or appspace server
        '''
        Query.__init__(self, appspace, *args, **kw)
        # appspace settings
        self._settings = self._appspace.manager.settings
        self._events = self._appspace.manager.events
        # enable for traits
        self._enable = True

    @property
    def _manage_class(self):
        return Appspace(Manager())

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
            return cls(Patterns.settings(
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

    def enable(self):
        '''toggle if trait events are allowed'''
        self.appendleft(setter(self, '_enable', not self._enable))
        return self

    def fire(self, event, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param event: event label
        '''
        self.appendleft(self._events.fire(event, *args, **kw))
        return self

    def localize(self, **kw):
        '''
        generate local component settings

        **kw: settings to add to local settings
        '''
        this = self._this
        metas = [b.Meta for b in getmro(getcls(this)) if hasattr(b, 'Meta')]
        meta = get_or_default(this, 'Meta')
        if meta:
            metas.append(meta)
        local_settings = self._settings.local[self.id().one()] = stuf(dict(
            (k, v) for k, v in self.members(m, lambda x: not x.startswith('_'))
        ) for m in metas)
        local_settings.update(kw)
        self.appendleft(local_settings)
        return self

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

    def setting(self, label, value=NoDefaultSpecified, default=None):
        '''
        change setting in application settings

        @param label: setting label
        @param value: value in settings (default: NoDefaultSpecified)
        @param default: setting value (default: None)
        '''
        if value is not NoDefaultSpecified:
            self._settings.set(label, value)
            return self
        self.appendleft(self._settings.get(label, default))
        return self

    def trigger(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        return self(self._events.react(label))

    def unbind(self, event, label, branch=False):
        '''
        unbind app from event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.unbind(event, self.app(label, branch).first())
        return self


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


__ = AppQuery
