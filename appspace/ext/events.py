# -*- coding: utf-8 -*-
'''extension event handling'''

from __future__ import absolute_import

from collections import deque
from operator import attrgetter, getitem

from appspace.keys import appifies, get_apps, apped

from .keys import AEventManager, AEvent


class Event(object):

    '''appspace event rules'''

    def __init__(self, label, priority=1, **kw):
        '''
        init

        @param label: event label
        @param priority: priority of event
        '''
        self.label = label
        self.priority = priority
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        return 'Event{label}@Priority{priority}'.format(
            label=self.label, priority=self.priority,
        )


@ appifies(AEventManager)
class EventManager(object):

    '''appspace event manager'''

    __slots__ = ('appspace', '_enabled')

    def __init__(self, appspace):
        '''
        init

        @param appspace: appspace to store events in
        '''
        self.appspace = appspace
        self._enabled = True

    def __repr__(self):
        return str(self.appspace.manager.lookupAll([AEvent], AEvent))

    def bind(self, label, app):
        '''
        bind app to event

        @param label: event label
        @param app: object to bind to event
        '''
        self.appspace.subscribe(AEvent, self.appspace.get(label), app)

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
        return results

    def get(self, label):
        '''
        returns event

        @param label: event label
        '''
        app = self.appspace.easy_lookup(AEvent, label)
        if app is not None:
            return getitem(get_apps(app), 0)
        return None

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
        class ANewEvent(AEvent):
            '''new event key'''
        class NewEvent(Event):
            '''event'''
        new_event = NewEvent(priority, **kw)
        apped(NewEvent, ANewEvent)
        self.appspace.easy_register(AEvent, label, new_event)
        return new_event

    def unbind(self, label, app):
        '''
        unbind app from event

        @param label: event label
        @param app: object to unbind from event
        '''
        self.appspace.unsubscribe(AEvent, self.appspace.get(label), app)

    def unregister(self, label):
        '''
        remove event

        @param label: event label
        '''
        self.appspace.easy_unregister(AEvent, label)


__all__ = ('Event', 'EventManager')
