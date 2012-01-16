# -*- coding: utf-8 -*-
# pylint: disable-msg=w0221
'''extension core classes'''

from __future__ import absolute_import

import uuid
from inspect import isclass
from operator import attrgetter, itemgetter
from collections import Mapping, Sequence, deque
from itertools import groupby, ifilter, ifilterfalse, imap

from appspace.utils import getcls
from appspace.managers import Manager
from appspace.builders import Appspace
from appspace.keys import AAppspace, apped
from appspace.error import ConfigurationError, NoAppError


class direct(object):

    '''passes application from appspace directly to host'''

    def __init__(self, label, branch=False):
        '''
        init

        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.label = label
        self.branch = branch

    def __get__(self, this, that):
        return Q(that).get(self.label, self.branch).one()

    def __set__(self, this, value):
        raise AttributeError('attribute is read-only')

    def __delete__(self, this):
        raise AttributeError('attribute is read-only')


class factory(direct):

    '''builds application stored in appspace and passes it to host'''

    def __init__(self, label, branch=False, *args, **kw):
        '''
        init

        @param label: application label
        @param branch: branch label (default: False)
        '''
        super(factory, self).__init__(label, branch)
        self.attrs = args
        self.extra = kw

    def __get__(self, this, that):
        new_app = super(factory, self).__get__(this, that)
        if isclass(new_app):
            attrs = [getattr(this, attr) for attr in self.attrs]
            new_app = new_app(*attrs, **self.extra)
            B(that).set(new_app, self.label, self.branch)
        return new_app


class Query(deque):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

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
                raise NoAppError('no appspace found')
        # appspace manager
        self._manager = self._appspace.manager
        deque.__init__(self, *args)

    def __call__(self, *args):
        return getcls(self)(self._appspace, *args, **dict(this=self._this))

    def _quikget(self, label, branch=False):
        if branch:
            return self._appspace[branch][label]
        return self._appspace[label]

    def get(self, label, branch=False):
        '''
        get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
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
        self.appendleft(self._appspace[label])
        return self

    def each(self, data, label, branch=False):
        '''
        run app in appsoace on each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.get(label, branch).first()
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
    
    @staticmethod
    def uuid():
        '''universal unique identifier'''
        return uuid.uuid4().hex.upper()
    

# query shortcut
Q = Query


class Builder(Query):

    '''appspace query'''

    @property
    def _manage_class(self):
        return Appspace(Manager())

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            return Query.branch(self, label)
        # create new branch
        except NoAppError:
            new_appspace = self._manage_class
            self._manager.set(label, new_appspace)
            self.appendleft(new_appspace)
            return self
        raise ConfigurationError('invalid branch configuration')
    
    def set(self, app, label, branch=False):
        '''
        add application to appspace

        @param app: new application

        @param label: application label
        @param branch: branch label (default: False)
        '''
        # use branch manager
        if branch:
            manager = Query.branch(self, branch).one().manager
        # use passed manager
        else:
            manager = self._manager
        # add to appspace
        manager.set(label, app)
        self.appendleft(app)
        return self

    @staticmethod
    def key(key, app):
        '''
        key an get

        @param key: key to key get
        @param get: get to key
        '''
        apped(app, key)
        return app


# builder shortcut
B = Builder

__all__ = ('B', 'Builder', 'Q', 'Query')
