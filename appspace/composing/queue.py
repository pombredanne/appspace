# -*- coding: utf-8 -*-
'''composing queue'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.building import BuildQueue

from .keys import NoDefault
from .mixin import ComposerMixin


class ComposerQueue(ComposerMixin, BuildQueue):

    '''application composing queue'''

    def burst(self, label, queue):
        '''
        process event subscribers on contents of queue

        @param label: event label
        @param queue: queued arguments
        '''
        self.outgoing.append(self._events.burst(label, queue))
        return self

    @lazy
    def composer(self):
        '''composer queue to attach to other apps'''
        return ComposerQueue(self.manager)

    def defaults(self):
        '''default settings by their lonesome'''
        self.outgoing.append(self._settings.defaults)
        return self

    def event(self, label, priority=False, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: False)
        '''
        # unregister event
        if not priority or not kw:
            self.manager.unregister(label)
            return self
        # register event if priority and keywords passed
        self.outgoing.append(self.manager.register(label, priority, **kw))
        return self

    def fire(self, label, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param label: event label
        '''
        self.outgoing.append(self._events.fire(label, *args, **kw))
        return self

    def react(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        self.outgoing.append(self._events.react(label))
        return self

    def required(self):
        '''required settings by their lonesome'''
        self.outgoing.append(self._settings.required)
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
        self.outgoing.append(self._settings.get(label, default))
        return self

    def trigger(self, label):
        '''
        get objects bound to an event

        @param label: event label
        '''
        self.outgoing.extend(self._events.react(label))
        return self


__all__ = ['ComposerQueue']
