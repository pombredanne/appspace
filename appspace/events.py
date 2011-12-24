# -*- coding: utf-8 -*-
'''events'''

from __future__ import absolute_import

from collections import deque
from functools import update_wrapper
from operator import attrgetter, getitem

from stuf.utils import setter

from .utils import get_appspace
from .core import AEventManager, AEvent, appifies, get_apps, apped


def on(*events):
    '''
    marks method as being a lazy component

    @param label: component label
    @param branch: component branch (default: None)
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class Event(object):

    '''event rules'''

    def __init__(self, label, priority=1, **kw):
        '''
        init

        @param label: event label
        @param priority: priority of event
        '''
        self.label = label
        self.priority = priority
        for k, v in kw.iteritems():
            setter(self, k, v)


class EventManager(object):

    appifies(AEventManager)

    __slots__ = ['a']

    def __init__(self, appspace):
        '''
        init

        @param appspace: appspace to store events in
        '''
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
        slen = len(subs)
        qlen = len(queue)
        if qlen != slen:
            raise ValueError('queue length {0} != event length {1}'.format(
                qlen, slen,
            ))
        results = []
        spop = subs.popleft
        qpop = queue.pop_left
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

    def get(self, label):
        '''
        returns event

        @param label: event label
        '''
        return getitem(get_apps(self.appspace.easy_lookup(AEvent, label)), 0)

    def react(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        subs = deque(i for i in sorted(
            self.appspace.subscribers(AEvent, self.get(label)),
            key=attrgetter('priority'),
        ))
        return subs

    def register(self, label, priority=1, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: 1)
        '''
        class ANewEvent(AEvent):  # pylint: disable-msg=w0232
            '''new event key'''
        class NewEvent(Event):
            '''event'''
        new_event = NewEvent(priority, **kw)
        apped(NewEvent, ANewEvent)
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


class On(object):

    '''attach events to method'''

    def __init__(self, method, *events):
        '''
        init

        @param method: method to tie to events
        @param *args: events
        '''
        self.events = events
        self.is_set = False
        self.method = method
        update_wrapper(self, method)

    def __get__(self, this, that):
        if not self.is_set:
            ebind = get_appspace(this, that).events.bind
            method = self.method
            for arg in self.events:
                ebind(arg, method)
            self.is_set = True
        return self.method
