# -*- coding: utf-8 -*-
'''composition query'''

from __future__ import absolute_import

from appspace.query import B
from appspace.ext import Manager, Composer
from appspace.query.keys import NoDefault
from appspace.error import ConfigurationError
from appspace.builders import Appspace, Patterns, patterns


class Query(B):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        B.__init__(self, appspace, *args, **kw)
        # appspace settings
        self._settings = self._space.manager.settings
        self._events = self._space.manager.events

    @property
    def _manage_class(self):
        # manager class
        return Appspace(Manager())

    @classmethod
    def appspace(cls, pattern, required=None, defaults=None, *args, **kw):
        '''
        build new appspace

        @param pattern: pattern configuration class or appspace label
        @param required: required settings (default: None)
        @param defaults: default settings (default: None)
        @param *args: tuple of module paths or inclusions
        '''
        # from appspace configuration class...
        if issubclass(pattern, Patterns):
            return cls(pattern.build(required, defaults))
        # from label and arguments...
        elif isinstance(pattern, basestring) and args:
            return cls(Composer.settings(
                patterns(pattern, *args, **kw), required, defaults,
            ))
        raise ConfigurationError('patterns not found')

    def bind(self, event, label, branch=False):
        '''
        bind get to event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.bind(event, self.get(label, branch).first())
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

    def fire(self, label, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param label: event label
        '''
        self.appendleft(self._events.fire(label, *args, **kw))
        return self

    def lock(self):
        '''lock settings so they are read only except locals'''
        self._settings.lock()

    def react(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        self.appendleft(self._events.react(label))
        return self

    def register(self, model):
        '''
        register model in appspace

        @param model: class to be model
        '''
        # attach manager
        setattr(model, 'A', self._space)
        # attach manager settings
        setattr(model, 'S', self._settings.final)
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
        self._events.unbind(event, self.get(label, branch).first())
        return self


__ = Query
__all__ = ['__']
