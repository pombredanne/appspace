# -*- coding: utf-8 -*-
'''query double queue queue'''

from __future__ import absolute_import

from functools import partial
from operator import itemgetter
from itertools import groupby, ifilter, ifilterfalse, imap

from stuf.utils import lazy, getcls

from appspace.ext.queue import namedqueue

from .query import Query


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
        self.__iter__ = self.outgoing.__iter__
        self.append = self.incoming.append
        self.appendleft = self.incoming.appendleft
        self.clear_incoming = self.incoming.clear
        self.clear_outgoing = self.outgoing.clear
        self.extend = self.incoming.extend
        self.extendleft = self.incoming.extendleft
        self.popleft = self.first = self.outgoing.popleft
        self.pop = self.last = self.outgoing.pop

    def __call__(self, *args):
        return getcls(self)(self.manager, *args, **dict(this=self._this))

    @lazy
    def querier(self):
        '''query queue to attach to other apps'''
        return DoubleQueue(self.manager)

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.outgoing.append(self._quikget(label, branch)(*args, **kw))
        return self

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        self.outgoing.append(self._getter(label))
        return self

    def callchain(self):
        '''execute a series of partials in the queue'''
        ar = self.append
        pl = self.incoming.popleft
        al = self.incoming.append
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
        self.append(partial(func, *args, **kw))
        return self

    def clear(self):
        '''clear all queues'''
        self.clear_incoming()
        self.clear_outgoing()

    def each(self, label, branch=False):
        '''
        run app in appsoace on each item in data

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extend(app(i) for i in self.incoming)
        return self

    def filter(self, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extend(ifilter(app, self.incoming))
        return self

    def find(self, label, branch=False):
        '''
        get first item in data for which app in appspace is true

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        for item in ifilter(app, self.incoming):
            self.outgoing.append(item)
            return self

    def firstone(self):
        '''fetch the first result and clear the queue'''
        value = self.first()
        self.outgoing.clear()
        return value

    def groupby(self, label, branch=False):
        '''
        group items from data by criteria of app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extend(groupby(self.incoming, app))
        return self

    def invoke(self, label, branch=False, *args, **kw):
        '''
        run app in appsoace on each item in data plus arbitrary args and
        keywords

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extend(app(i, *args, **kw) for i in self.incoming)
        return self

    def iterincoming(self):
        '''iterate over incoming queue'''
        return self.incoming.__iter__()

    def lastone(self):
        '''fetch the last result and clear the queue'''
        value = self.pop()
        self.outgoing.clear()
        return value

    def map(self, label, branch=False):
        '''
        apply app in appspace to each item in data

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extend(imap(app, self.incoming))
        return self

    def max(self, label, branch=False):
        '''
        find maximum by key function in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.append(max(self.incoming, key=app))
        return self

    def members(self, test):
        '''
        fetch object members by class

        @param tester: test to filter by (default: False)
        '''
        self.outgoing.extend(
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
        value = self.outgoing.popleft()
        # clear queue
        self.outgoing.clear()
        return value

    def pluck(self, key):
        '''
        get items from data by key

        @param key: key to search for
        @param data: data to process
        '''
        plucker = itemgetter(key)
        self.outgoing.extend(ifilter(
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
        self.outgoing.append(reduce(app, self.incoming, initial))
        return self

    def reject(self, label, branch=False):
        '''
        fetch items from data for which app in appspace is False

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extend(ifilterfalse(app, self.incoming))
        return self

    def right(self, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace from right side

        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = lambda x, y: self._quikget(label, branch)(y, x)
        self.outgoing.append(reduce(app, reversed(self.incoming), initial))
        return self

    def sorted(self, label, branch=False):
        '''
        sort by key app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.outgoing.extend(sorted(self.incoming, key=app))
        return self


__all__ = ['DoubleQueue']
