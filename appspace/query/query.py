# -*- coding: utf-8 -*-
'''query'''

from __future__ import absolute_import

from operator import attrgetter, itemgetter
from collections import Mapping, Sequence, deque
from itertools import groupby, ifilter, ifilterfalse, imap

from stuf.utils import getcls

from appspace.keys import AAppspace
from appspace.error import NoAppError


class Query(deque):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        try:
            # fetch appspace from class
            self._space = appspace.A
            # save the host class
            self._this = appspace
        except (AttributeError, NoAppError):
            # standalone appspace
            if AAppspace.providedBy(appspace):
                self._space = appspace
                self._this = kw.pop('this', None)
            else:
                raise NoAppError('no appspace found')
        # appspace manager
        self._manager = self._space.manager
        deque.__init__(self, *args)

    def __call__(self, *args):
        return getcls(self)(self._space, *args, **dict(this=self._this))

    def _quikget(self, label, branch=False):
        return self._space[branch][label] if branch else self._space[label]

    def get(self, label, branch=False):
        '''
        get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.appendleft(self._quikget(label, branch))
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
        self.appendleft(self._space[label])
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

    first = deque.popleft

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

    @staticmethod
    def itermembers(this):
        '''
        iterate over object members

        @param this: an object
        '''
        for key in dir(this):
            if not any([key.startswith('__'), key.isupper()]):
                try:
                    value = getattr(this, key)
                except AttributeError:
                    pass
                else:
                    yield key, value

    @staticmethod
    def iskey(key):
        '''validate key'''
        return all([not key.startswith('_'), not key.isupper()])

    @classmethod
    def keyed(cls, key, this):
        '''
        check if item provides an app key

        @param label: app key
        @param this: object to check
        '''
        return cls.keyer(key, this[1])

    @staticmethod
    def keyer(key, this):
        '''
        check if item provides an app key

        @param label: app key
        @param this: object to check
        '''
        try:
            return key.providedBy(this)
        except (AttributeError, TypeError):
            try:
                return key.implementedBy(this)
            except (AttributeError, TypeError):
                return False

    last = deque.pop

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

    @staticmethod
    def plucker(key, data):
        '''
        fetch item from data structure by key

        @param key: label of item
        @param data: data containing item
        '''
        return itemgetter(key) if isinstance(
            data, (Mapping, Sequence)
        ) else attrgetter(key)

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


Q = Query
__all__ = ['Q']
