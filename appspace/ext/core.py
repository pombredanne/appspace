# -*- coding: utf-8 -*-
'''appspace extension query'''

from __future__ import absolute_import

from operator import attrgetter, itemgetter
from collections import Mapping, Sequence, deque
from itertools import groupby, ifilter, ifilterfalse, imap

from appspace.utils import getcls
from appspace.keys import AAppspace, apped
from appspace.error import ConfigurationError, NoAppError

__all__ = ['Query']


class Query(deque):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: appspace or appspace server
        '''
        try:
            # fetch appspace from class
            self._appspace = appspace.A
            # save the host class
            self._this = appspace
        except (AttributeError, NoAppError):
            # standalone appspace
            if AAppspace.providedBy(appspace):
                self._appspace = appspace
                self._this = kw.pop('this', None)
            else:
                raise NoAppError('appspace not found')
        # appspace manager
        self._manager = self._appspace.manager
        deque.__init__(self, *args)

    def __call__(self, *args):
        return getcls(self)(self._appspace, *args, **dict(this=self._this))

    def app(self, label, branch=False, app=False):
        '''
        add or get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        @param app: new application (default: False)
        '''
        # process new application
        if app:
            # use branch manager
            if branch:
                manager = self.branch(branch).one().manager
            # use passed manager
            else:
                manager = self._manager
            # add to appspace
            manager.set(label, app)
            self.appendleft(app)
            return self
        # return app from branch
        if branch:
            self.appendleft(self._appspace[branch][label])
            return self
        # return from primary appsapce
        self.appendleft(self._appspace[label])
        return self

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.appendleft(self._appspace[branch][label](*args, **kw))
        return self

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            self.appendleft(self._appspace[label])
            return self
        # create new branch
        except NoAppError:
            new_appspace = self._manage_class()
            self._manager.set(label, new_appspace)
            self.appendleft(new_appspace)
            return self
        raise ConfigurationError('invalid branch configuration')

    def each(self, data, label, branch=False):
        '''
        run app in appsoace on each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
        return self(app(i) for i in data)

    def find(self, data, label, branch=False):
        '''
        get first item in data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
        for item in ifilter(app, data):
            self.appendleft(item)
            return self

    def filter(self, data, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
        return self(ifilter(app, data))

    def first(self):
        '''fetch one result'''
        try:
            value = self.popleft()
            # clear queue
            return value
        except IndexError:
            return []

    def groupby(self, data, label, branch=False):
        '''
        group items from data by criteria of app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
        return self(groupby(data, app))

    def invoke(self, data, label, branch=False, *args, **kw):
        '''
        run app in appsoace on each item in data plus arbitrary args and
        keywords

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
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
    def key(key, app):
        '''
        key an app

        @param key: key to key app
        @param app: app to key
        '''
        apped(app, key)

    @staticmethod
    def keyed(key, this):
        '''
        check if item provides an app key

        @param label: app key
        @param this: object to check
        '''
        try:
            return key.providedBy(this[1])
        except (AttributeError, TypeError):
            try:
                return key.implementedBy(this[1])
            except (AttributeError, TypeError):
                return False

    def last(self):
        '''fetch the last result'''
        try:
            return self.pop()
        except IndexError:
            return []

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
        app = self.app(label, branch).first()
        return self(imap(app, data))

    def max(self, data, label, branch=False):
        '''
        find maximum by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
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
        app = self.app(label, branch).first()
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
        getit = itemgetter(key) if isinstance(
            data, (Mapping, Sequence)
        ) else attrgetter(key)
        try:
            return getit(data)
        except (AttributeError, IndexError):
            return None

    def pluck(self, key, data):
        '''
        get items from data by key

        @param key: key to search for
        @param data: data to process
        '''
        return self(ifilter(
            lambda x: x is not None, (self.plucker(key, i) for i in data),
        ))

    def reduce(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = self.app(label, branch).first()
        self.appendleft(reduce(app, data, initial))
        return self

    def reject(self, data, label, branch=False):
        '''
        fetch items from data for which app in appspace is false

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
        return self(ifilterfalse(app, data))

    def right(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace from right side

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = lambda x, y: self.app(label, branch).first()(y, x)
        self.appendleft(reduce(app, reversed(data), initial))
        return self

    def sorted(self, data, label, branch=False):
        '''
        sort by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app(label, branch).first()
        return self(sorted(data, key=app))
