# -*- coding: utf-8 -*-
'''composing query'''

from __future__ import absolute_import


from appspace.error import ConfigurationError
from appspace.spaces import Patterns, patterns
from appspace.ext.query.builder import Builder
from appspace.ext.core.builders import Composer, Manager

from .keys import NoDefault


class ComposerQuery(Builder):

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        super(ComposerQuery, self).__init__(appspace, *args, **kw)
        # appspace settings
        self._settings = self.manager.settings
        self._events = self.manager.events

    @property
    def _manage_class(self):
        # manager class
        return Manager()

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
        return self._events.burst(label, queue)

    def defaults(self):
        '''default settings by their lonesome'''
        return self._settings.defaults

    def event(self, label, priority=False, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: False)
        '''
        # unregister event
        if not priority or not kw:
            self._events.unregister(label)
        # register event if priority and keywords passed
        self._events.register(label, priority, **kw)

    def fire(self, label, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param label: event label
        '''
        return self._events.fire(label, *args, **kw)

    def lock(self):
        '''lock settings so they are read only except locals'''
        self._settings.lock()

    def react(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        return self._events.react(label)

    def register(self, model):
        '''
        register model in appspace

        @param model: class to be model
        '''
        # attach manager
        model.A = self.manager
        # attach manager settings
        model.S = self._settings.final
        return self

    def required(self):
        '''required settings by their lonesome'''
        return self._settings.required

    def setting(self, label, value=NoDefault, default=None):
        '''
        change setting in application settings

        @param label: setting label
        @param value: value in settings (default: NoDefault)
        @param default: setting value (default: None)
        '''
        if value is not NoDefault:
            self._settings.set(label, value)
        return self._settings.get(label, default)

    def trigger(self, label):
        '''
        get applications bound to an event

        @param label: event label
        '''
        return self._events.react(label)

    def unbind(self, event, label, branch=False):
        '''
        unbind application from event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.unbind(event, self.get(label, branch).first())
        return self


__all__ = ['ComposerQuery']
