# -*- coding: utf-8 -*-
## pylint: disable-msg=f0401,w0232
'''events'''

from __future__ import absolute_import

from collections import deque
from operator import attrgetter, getitem

from stuf.utils import setter
from zope.interface import implements, directlyProvides, providedBy

from .keys import AEventManager, AEvent


class Event(object):

    '''event rules'''

    def __init__(self, label, priority=1, **kw):
        self.priority = priority
        self.label = label
        for k, v in kw.iteritems():
            setter(self, k, v)


class EventManager(object):

    implements(AEventManager)

    __slots__ = ['a']

    def __init__(self, appspace):
        self.a = appspace

    def bind(self, label, component):
        '''
        bind component to event

        @param label: event label
        @param component: object to bind to event
        '''
        self.appspace.subscribe(AEvent, self.appspace.get(label), component)

    def burst(self, label, queue):
        '''
        run event subscribers on contents of queue

        @param label: event label
        @param queue: queued arguments
        '''
        subs = self.react(label)
        if len(subs) != len(queue):
            raise ValueError('queue length {0} != event length {1}'.format(
                len(queue), len(subs),
            ))
        queue.reverse()
        results = []
        spop = subs.pop
        qpop = queue.pop_right
        while subs and queue:
            args = qpop()[-1]
            if len(args) == 2:
                results.append(spop()(*args[0], **args[-1]))
        return results

    def fire(self, event, *args, **kw):
        '''
        fire event, passing arbitrary positional arguments and keywords

        @param event: event label
        '''
        subs = self.appspace.react(event)
        spop = subs.pop
        results = []
        rappend = results.append
        while subs:
            rappend(spop()(*args, **kw))
        return results

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
        subs = deque(i for i in sorted(
            self.appspace.subscribers(AEvent, self.get(label)),
            key=attrgetter('priority'),
        ))
        subs.reverse()
        return subs

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
        directlyProvides(NewEvent, ANewEvent)
        self.appspace.easy_register(AEvent, label, new_event)

    def unbind(self, label, component):
        '''
        unbind component from event

        @param label: event label
        @param component: object to unbind from event
        '''
        self.appspace.unsubscribe(AEvent, self.appspace.get(label), component)

    def unregister(self, label):
        '''
        remove event

        @param label: event label
        '''
        self.appspace.easy_unregister(AEvent, label)
