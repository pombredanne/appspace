# -*- coding: utf-8 -*-
'''composing query'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.building import BuildQuery

from .keys import NoDefault
from .mixin import ComposerMixin


class ComposerQuery(ComposerMixin, BuildQuery):

    '''application composing query'''

    @lazy
    def composer(self):
        '''composer to attach to other apps'''
        return ComposerQuery(self.manager)

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

    def react(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        return self._events.react(label)

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


__all__ = ['ComposerQuery']
