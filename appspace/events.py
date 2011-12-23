# -*- coding: utf-8 -*-
## pylint: disable-msg=f0401,w0232
'''appspace events'''

from __future__ import absolute_import

from operator import getitem

from stuf.utils import setter
from zope.interface import (
    implements as appifies, directlyProvides as cls_appify, providedBy
)

from .keys import AEventManager, AEvent


class Event(object):

    def __init__(self, label, priority=1, **kw):
        self.priority = priority
        self.label = label
        for k, v in kw.iteritems():
            setter(self, k, v)


class EventManager(object):

    appifies(AEventManager)

    def __init__(self, appspace):
        self.appspace = appspace

    def bind(self, label, component):
        '''
        bind component to event

        @param label: event label
        @param component: object to bind to event
        '''
        self.appspace.subscribe(AEvent, self.appspace.get(label), component)

    def fire(self, event, *args, **kw):
        '''
        fire event, passing arbitrary positional arguments and keywords

        @param appspace: existing appspace
        @param event: event label
        '''
        for handler in self.appspace.react(event):
            handler(*args, **kw)

    def get(self, label):
        '''
        returns event

        @param label: event label
        '''
        return getitem(providedBy(self.appspace.easy_lookup(AEvent, label)), 0)

    def react(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        return self.appspace.subscribers(AEvent, self.get(label))

    def register(self, label, priority=1, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: 1)
        '''
        class ANewEvent(AEvent):
            '''new event key'''

        class NewEvent(Event):
            '''event'''

        new_event = NewEvent(priority, **kw)
        cls_appify(NewEvent, ANewEvent)
        self.appspace.easy_register(AEvent, label, new_event)
