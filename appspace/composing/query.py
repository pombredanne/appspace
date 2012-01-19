# -*- coding: utf-8 -*-
'''composing query'''

from __future__ import absolute_import

from .keys import NoDefault
from appspace.build import B
from .mixin import ComposerMixin


class Composer(ComposerMixin, B):

    '''appspace composer'''

    def bind(self, event, label, branch=False):
        '''
        bind get to event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self._events.bind(event, self.get(label, branch))

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
            self._manager.unregister(label)
        # register event if priority and keywords passed
        self._manager.register(label, priority, **kw)

    def fire(self, label, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param label: event label
        '''
        return self._events.fire(label, *args, **kw)

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
        setattr(model, 'A', self._manager)
        # attach manager settings
        setattr(model, 'S', self._settings.final)

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
        get objects bound to an event

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
        self._events.unbind(event, self.get(label, branch))


__ = Composer
__all__ = ['__']
