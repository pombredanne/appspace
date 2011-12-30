# -*- coding: utf-8 -*-
'''appspace events'''

from __future__ import absolute_import

from collections import deque
from operator import attrgetter, getitem
from inspect import ismethod, getargspec

from stuf.utils import setter

from .error import TraitError
from .core import AEventManager, AEvent, appifies, get_apps, apped


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
            setter(self, k, v)

    def __repr__(self):
        return 'Event{label}@Priority{priority}'.format(
            label=self.label, priority=self.priority,
        )


class EventManager(object):

    '''appspace event manager'''

    __slots__ = ['a', '_enabled']

    appifies(AEventManager)

    def __init__(self, appspace):
        '''
        init

        @param appspace: appspace to store events in
        '''
        self.a = appspace
        self._enabled = True

    def __repr__(self):
        return str(self.appspace.manager.lookupAll(AEvent, AEvent))

    @property
    def enabled(self):
        '''are trait events allowed'''
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        '''
        enable trait events

        @param value: True or False
        '''
        self._enabled = value

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
        class ANewEvent(AEvent):
            '''new event key'''
        class NewEvent(Event):
            '''event'''
        new_event = NewEvent(priority, **kw)
        apped(NewEvent, ANewEvent)
        self.appspace.easy_register(AEvent, label, new_event)
        return new_event

    def trait(self, label, old_value, new_value):
        '''
        process trait related event

        @param label: trait event label
        @param old_value: old trait value
        @param new_value: new trait value
        '''
        if self.enabled:
            # First dynamic ones
            callables = self.react(label)
            # Call them all now
            for C in callables:
                # Traits catches and logs errors here.  I allow them to raise
                if callable(C):
                    argspec = getargspec(C)
                    nargs = len(argspec[0])
                    # Bound methods have an additional 'self' argument
                    # I don't know how to treat unbound methods, but they
                    # can't really be used for callbacks.
                    if ismethod(C):
                        offset = -1
                    else:
                        offset = 0
                    if nargs + offset == 0:
                        C()
                    elif nargs + offset == 1:
                        C(label)
                    elif nargs + offset == 2:
                        C(label, new_value)
                    elif nargs + offset == 3:
                        C(label, old_value, new_value)
                    else:
                        raise TraitError(
                            'trait changed callback must have 0-3 arguments'
                        )
                else:
                    raise TraitError('trait changed callback must be callable')

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
