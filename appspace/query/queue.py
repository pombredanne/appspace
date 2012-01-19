# -*- coding: utf-8 -*-
'''query queue'''

from __future__ import absolute_import

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


__all__ = ['Queue']
