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
        self.last = self.pop
        self.first = self.popleft

    def __call__(self, *args):
        return getcls(self)(self.manager, *args, **dict(this=self._this))

    @lazy
    def querier(self):
        '''query queue to attach to other apps'''
        return Queue(self.manager)

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.append(self._quikget(label, branch)(*args, **kw))
        return self

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        self.append(self._getter(label))
        return self

    def each(self, data, label, branch=False):
        '''
        run app in appsoace on each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.extend(app(i) for i in data)
        return self

    def filter(self, data, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.extend(ifilter(app, data))
        return self

    def find(self, data, label, branch=False):
        '''
        get first item in data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        for item in ifilter(app, data):
            self.append(item)
            return self

    def firstone(self):
        '''fetch the first result and clear the queue'''
        value = self.first()
        self.clear()
        return value

    def get(self, label, branch=False):
        '''
        get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.append(
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
        self.extend(groupby(data, app))
        return self

    def invoke(self, data, label, branch=False, *args, **kw):
        '''
        run app in appsoace on each item in data plus arbitrary args and
        keywords

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.extend(app(i, *args, **kw) for i in data)
        return self

    def lastone(self):
        '''fetch the last result and clear the queue'''
        value = self.last()
        self.clear()
        return value

    def map(self, data, label, branch=False):
        '''
        apply app in appspace to each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.extend(imap(app, data))
        return self

    def max(self, data, label, branch=False):
        '''
        find maximum by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.append(max(data, key=app))
        return self

    def members(self, test):
        '''
        fetch object members by class

        @param tester: test to filter by (default: False)
        '''
        self.extend(ifilter(test, self.itermembers(self._this)))
        return self

    def min(self, data, label, branch=False):
        '''
        find minimum value by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.append(min(data, key=app))
        return self

    def pluck(self, key, data):
        '''
        get items from data by key

        @param key: key to search for
        @param data: data to process
        '''
        plucker = self.plucker(key, data)
        self.extend(ifilter(
            lambda x: x is not None, (plucker(i) for i in data),
        ))
        return self

    def reduce(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = self._quikget(label, branch)
        self.append(reduce(app, data, initial))
        return self

    def reject(self, data, label, branch=False):
        '''
        fetch items from data for which app in appspace is false

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._quikget(label, branch)
        self.extend(ifilterfalse(app, data))
        return self

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
        self.extend(sorted(data, key=self._quikget(label, branch)))
        return self


__all__ = ['Queue']
