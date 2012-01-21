# -*- coding: utf-8 -*-
'''query queue'''

from __future__ import absolute_import

from functools import partial
from operator import itemgetter
from itertools import groupby, ifilter, ifilterfalse, imap

from stuf.utils import getcls, lazy

from appspace.ext.queue import namedqueue

from .query import Query


class Queue(Query, namedqueue):

    '''query queue'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        Query.__init__(self, appspace, **kw)
        namedqueue.__init__(self, *args, **kw)

    def __call__(self, *args):
        return getcls(self)(self.manager, *args, **dict(this=self._this))

    @lazy
    def querier(self):
        '''query queue to attach to other apps'''
        return Queue(self.manager)

    _quikget = Query._q_get

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.appendleft(self._quikget(label, branch)(*args, **kw))
        return self

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        self.appendleft(self._getter(label))
        return self

    def each(self, data, label, branch=False):
        '''
        run app in appsoace on each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        return self(app(i) for i in data)

    def filter(self, data, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        return self(ifilter(app, data))

    def find(self, data, label, branch=False):
        '''
        get first item in data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        for item in ifilter(app, data):
            self.appendleft(item)
            return self

    first = namedqueue.popleft

    def firstone(self):
        '''fetch the first result and clear the queue'''
        try:
            value = self.popleft()
            self.clear()
            return value
        except IndexError:
            return []

    def get(self, label, branch=False):
        '''
        get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.appendleft(
            self._getter(branch)[label] if branch else self._getter(label)
        )
        return self

    def groupby(self, data, label, branch=False):
        '''
        group items from data by criteria of app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        return self(groupby(data, app))

    def invoke(self, data, label, branch=False, *args, **kw):
        '''
        run app in appsoace on each item in data plus arbitrary args and
        keywords

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        return self(app(i, *args, **kw) for i in data)

    last = namedqueue.pop

    def lastone(self):
        '''fetch the last result and clear the queue'''
        try:
            value = self.pop()
            self.clear()
            return value
        except IndexError:
            return []

    def map(self, data, label, branch=False):
        '''
        apply app in appspace to each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        return self(imap(app, data))

    def max(self, data, label, branch=False):
        '''
        find maximum by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.appendleft(max(data, key=app))
        return self

    def members(self, test):
        '''
        fetch object members by class

        @param tester: test to filter by (default: False)
        '''
        return self(ifilter(test, self.itermembers(self._this)))

    def min(self, data, label, branch=False):
        '''
        find minimum value by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.appendleft(min(data, key=app))
        return self

    def one(self):
        '''fetch one result'''
        try:
            value = self.popleft()
            # clear queue
            self.clear()
            return value
        except IndexError:
            return []

    def pluck(self, key, data):
        '''
        get items from data by key

        @param key: key to search for
        @param data: data to process
        '''
        plucker = self.plucker(key, data)
        return self(ifilter(
            lambda x: x is not None, (plucker(i) for i in data),
        ))

    def reduce(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = self._quikget(label, branch)
        self.appendleft(reduce(app, data, initial))
        return self

    def reject(self, data, label, branch=False):
        '''
        fetch items from data for which app in appspace is false

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        return self(ifilterfalse(app, data))

    def right(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace from right side

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = lambda x, y: self._quikget(label, branch)(y, x)
        self.appendleft(reduce(app, reversed(data), initial))
        return self

    def sorted(self, data, label, branch=False):
        '''
        sort by key app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        return self(sorted(data, key=app))
    
    
class DoubleQueue(Query):

    '''query queue'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        super(DoubleQueue, self).__init__(appspace, **kw)
        self.incoming = namedqueue(*args, **kw)
        self.outgoing = namedqueue(**kw)

    def __call__(self, *args):
        return getcls(self)(self.manager, *args, **dict(this=self._this))
    
    def __iter__(self):
        return self.outgoing.__iter__()

    @lazy
    def querier(self):
        '''query queue to attach to other apps'''
        return DoubleQueue(self.manager)
    
    def append(self, item):
        '''
        append to right side of incoming queue
        
        @param item: item to append
        '''
        self.incoming.append(item)
        
    def appendleft(self, item):
        '''
        append to left side of incoming queue
        
        @param item: item to append
        '''
        self.incoming.appendleft(item)
        
    _quikget = Query._q_get

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.outgoing.appendleft(self._quikget(label, branch)(*args, **kw))
        return self

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        self.outgoing.appendleft(self._getter(label))
        return self

    def callchain(self):
        '''execute a series of partials in the queue'''
        ar = self.outgoing.append
        pl = self.incoming.popleft()
        al = self.incoming.append()
        for i in xrange(len(self.incoming)):
            call = pl()
            ar(call())
            al(call)
        return self

    def chain(self, func, *args, **kw):
        '''
        partialize a function with argumetns and keywords and add to
        application queue

        @param func: function or method
        '''
        self.incoming.append(partial(func, *args, **kw))
        return self
    
    def clear(self):
        '''clear all queues'''
        self.incoming.clear()
        self.outgoing.clear()
    
    def clear_incoming(self):
        '''clear incoming queue'''
        self.incoming.clear()
        
    def clear_outgoing(self):
        '''clear outgoing queue'''
        self.outgoing.clear()

    def each(self, label, branch=False):
        '''
        run app in appsoace on each item in data

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extendleft(app(i) for i in self.incoming)
        return self

    def filter(self, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extendleft(ifilter(app, self.incoming))
        return self

    def find(self, label, branch=False):
        '''
        get first item in data for which app in appspace is true

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        for item in ifilter(app, self.incoming):
            self.outgoing.appendleft(item)
            return self

    def first(self):
        '''fetch the first result'''
        return self.outgoing.popleft()
    
    def firstone(self):
        '''fetch the first result and clear the queue'''
        value = self.outgoing.popleft()
        self.outgoing.clear()
        return value

    def get(self, label, branch=False):
        '''
        get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.outgoing.appendleft(
            self._getter(branch)[label] if branch else self._getter(label)
        )
        return self

    def groupby(self, label, branch=False):
        '''
        group items from data by criteria of app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extendleft(groupby(self.incoming, app))
        return self

    def invoke(self, label, branch=False, *args, **kw):
        '''
        run app in appsoace on each item in data plus arbitrary args and
        keywords

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extendleft(app(i, *args, **kw) for i in self.incoming)
        return self
    
    def iterincoming(self):
        '''iterate over incoming queue'''
        return self.incoming.__iter__()

    def last(self):
        '''fetch the last result'''
        return self.outgoing.pop()

    def lastone(self):
        '''fetch the last result and clear the queue'''
        value = self.outgoing.pop()
        self.outgoing.clear()
        return value

    def map(self, label, branch=False):
        '''
        apply app in appspace to each item in data

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extendleft(imap(app, self.incoming))
        return self

    def max(self, label, branch=False):
        '''
        find maximum by key function in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.appendleft(max(self.incoming, key=app))
        return self

    def members(self, test):
        '''
        fetch object members by class

        @param tester: test to filter by (default: False)
        '''
        self.outgoing.extendleft(
            ifilter(test, self.itermembers(self._this))
        )
        return self

    def min(self, label, branch=False):
        '''
        find minimum value by key function in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.appendleft(min(self.incoming, key=app))
        return self

    def one(self):
        '''fetch one result'''
        try:
            value = self.outgoing.popleft()
            # clear queue
            self.outgoing.clear()
            return value
        except IndexError:
            return []

    def pluck(self, key):
        '''
        get items from data by key

        @param key: key to search for
        @param data: data to process
        '''
        plucker = itemgetter(key)
        self.outgoing.extendleft(ifilter(
            lambda x: x is not None, (plucker(i) for i in self.incoming),
        ))
        return self

    def reduce(self, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = self._quikget(label, branch)
        self.outgoing.appendleft(reduce(app, self.incoming, initial))
        return self

    def reject(self, label, branch=False):
        '''
        fetch items from data for which app in appspace is False

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extendleft(ifilterfalse(app, self.incoming))
        return self

    def right(self, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace from right side

        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = lambda x, y: self._quikget(label, branch)(y, x)
        self.appendleft(reduce(app, reversed(self.incoming), initial))
        return self

    def sorted(self, label, branch=False):
        '''
        sort by key app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extendleft(sorted(self.incoming, key=app))
        return self


Q2 = DoubleQueue
__all__ = ['2Q', 'Queue']
