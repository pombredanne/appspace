# -*- coding: utf-8 -*-
'''query queue'''

from __future__ import absolute_import

from functools import partial
from operator import itemgetter
from contextlib import contextmanager
from itertools import groupby, ifilter, ifilterfalse, imap

from stuf.utils import lazy

from appspace.ext import namedqueue

from .query import QueryMixin
from .context import AppContext


class Queue(QueryMixin):

    '''query queue'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        super(Queue, self).__init__(appspace, **kw)
        self.max_length = kw.pop('max_length', None)
        self.incoming = namedqueue(self.max_length, *args)
        self.outgoing = namedqueue(self.max_length)
        self.calls = namedqueue(self.max_length)
        self._tmp = namedqueue(self.max_length)
        self.__iter__ = self.outgoing.__iter__
        self.append = self.incoming.append
        self.appendleft = self.incoming.appendleft
        self._clear_tmp = self._tmp.clear
        self._tmpappend = self._tmp.append
        self._tmpappendleft = self._tmp.appendleft
        self.clear_calls = self.calls.clear
        self.clear_incoming = self.incoming.clear
        self.clear_outgoing = self.outgoing.clear
        self.extend = self.incoming.extend
        self.extendleft = self.incoming.extendleft
        self.iterincoming = self.incoming.__iter__
        self.outappend = self.outgoing.append
        self.outextend = self.outgoing.extend
        self.pop = self.last = self.outgoing.pop
        self.popleft = self.first = self.outgoing.popleft

    @lazy
    def queuer(self):
        '''query queue to attach to other apps'''
        return Queue(self.manager)

    def app(self, label, branch=False):
        '''
        wrap app in context manager

        @param label: application label
        @param branch: branch label (default: False)
        '''
        return AppContext(self, label, branch)

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.sync():
            self.outappend(self._qget(label, branch)(*args, **kw))
        return self

    def applychain(self, label, branch=False, *args, **kw):
        '''
        partialize a callable from appspace with arguments and keywords
        and add to application queue

        @param func: function or method
        '''
        self.calls.append(partial(self._qapply, label, branch, *args, **kw))
        return self

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        with self.sync():
            self.outappend(self._getter(label))
        return self

    def callchain(self):
        '''execute a series of partials in the queue'''
        with self.sync():
            calls = self.calls
            outappend = self.outappend
            callpopleft = self.calls.popleft
            tmpappend = self._tmpappend
            while calls:
                call = callpopleft()
                outappend(call())
                tmpappend(call)
            calls.extend(self._tmp)
        return self

    def chain(self, func, *args, **kw):
        '''
        partialize a function with argumetns and keywords and add to
        application queue

        @param func: function or method
        '''
        self.calls.append(partial(func, *args, **kw))
        return self

    def clear(self):
        '''clear all queues'''
        self._clear_tmp()
        self.clear_incoming()
        self.clear_outgoing()
        self.clear_calls()

    def each(self, label, branch=False):
        '''
        run app in appspace on each item in data

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outextend(app(i) for i in self.incoming)
        return self

    def filter(self, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outgoing.extend(ifilter(app, self.incoming))
        return self

    def find(self, label, branch=False):
        '''
        get first item in data for which app in appspace is true

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            for item in ifilter(app, self.incoming):
                self.outappend(item)
                self.sync()
                return self

    def firstone(self):
        '''fetch the first result and clear the queue'''
        value = self.first()
        self.clear_outgoing()
        return value

    def groupby(self, label, branch=False):
        '''
        group items from data by criteria of app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outextend(groupby(self.incoming, app))
        return self

    def invoke(self, label, branch=False, *args, **kw):
        '''
        run app in appsoace on each item in data plus arbitrary args and
        keywords

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outextend(app(i, *args, **kw) for i in self.incoming)
        return self

    def lastone(self):
        '''fetch the last result and clear the queue'''
        value = self.last()
        self.clear_outgoing()
        return value

    def map(self, label, branch=False):
        '''
        apply app in appspace to each item in data

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outextend(imap(app, self.incoming))
        return self

    def max(self, label, branch=False):
        '''
        find maximum by key function in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outappend(max(self.incoming, key=app))
        return self

    def members(self, test):
        '''
        fetch object members by class

        @param tester: test to filter by (default: False)
        '''
        with self.sync():
            self.outextend(ifilter(test, self.itermembers(self._this)))
        return self

    def min(self, label, branch=False):
        '''
        find minimum value by key function in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outappend(min(self.incoming, key=app))
        return self

    def one(self):
        '''fetch one result'''
        value = self.first()
        # clear queue
        self.clear_outgoing()
        return value

    def pluck(self, key):
        '''
        get items from data by key

        @param key: key to search for
        @param data: data to process
        '''
        with self.sync():
            plucker = itemgetter(key)
            self.outextend(ifilter(
                lambda x: x is not None, (plucker(i) for i in self.incoming),
            ))
        return self
    
    def queue(self, app):
        '''
        add query to app

        @param app: app to add query to
        '''
        app._U = self.queuer

    def reduce(self, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        with self.app(label, branch) as app:
            self.outappend(reduce(app, self.incoming, initial))
        return self

    def reject(self, label, branch=False):
        '''
        fetch items from data for which app in appspace is False

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outextend(ifilterfalse(app, self.incoming))
        return self

    def right(self, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace from right side

        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        with self.app(label, branch) as app:
            app = lambda x, y: app(y, x)
            self.outappend(reduce(app, reversed(self.incoming), initial))
        return self

    def sorted(self, label, branch=False):
        '''
        sort by key app in appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        with self.app(label, branch) as app:
            self.outextend(sorted(self.incoming, key=app))
        return self
    
    @contextmanager
    def sync(self):
        '''sync incoming queue with outgoing queue'''
        self._clear_tmp()
        try:
            yield
            self.clear_incoming()
            self.extend(self.outgoing)
        except:
            self.clear_outgoing()
            raise
        finally:
            self._clear_tmp()


__all__ = ['Queue']
