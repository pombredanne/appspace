# -*- coding: utf-8 -*-
'''composing queue'''

from __future__ import absolute_import

from appspace.build import BuildQueue

from .keys import NoDefault
from .mixin import ComposerMixin


class ComposerQueue(ComposerMixin, BuildQueue):

    '''composer with queue'''

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


__all__ = ['ComposerQueue']
