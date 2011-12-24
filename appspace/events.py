# -*- coding: utf-8 -*-
'''events'''

from __future__ import absolute_import

from collections import deque
from functools import update_wrapper
from operator import attrgetter, getitem
from inspect import ismethod, getargspec

from stuf.utils import setter

from .error import TraitError
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

    __slots__ = ['a', '_enabled']

    def __init__(self, appspace):
        '''
        init

        @param appspace: appspace to store events in
        '''
        self.a = appspace
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

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

    def trait(self, name, old_value, new_value):
        # First dynamic ones
        callables = self.react(name)
        # Call them all now
        for c in callables:
            # Traits catches and logs errors here.  I allow them to raise
            if callable(c):
                argspec = getargspec(c)
                nargs = len(argspec[0])
                # Bound methods have an additional 'self' argument
                # I don't know how to treat unbound methods, but they
                # can't really be used for callbacks.
                if ismethod(c):
                    offset = -1
                else:
                    offset = 0
                if nargs + offset == 0:
                    c()
                elif nargs + offset == 1:
                    c(name)
                elif nargs + offset == 2:
                    c(name, new_value)
                elif nargs + offset == 3:
                    c(name, old_value, new_value)
                else:
                    raise TraitError(
                        'trait changed callback must have 0-3 arguments'
                    )
            else:
                raise TraitError('trait changed callback must be callable')

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
