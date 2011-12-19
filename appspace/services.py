# -*- coding: utf-8 -*-
# pylint: disable-msg=f0401
'''services'''

from __future__ import absolute_import
from collections import deque

from zope.interface import implements as appifies

from .keys import AQueue, ALazyApp


class LazyApp(object):

    '''lazy component loader'''

    appifies(ALazyApp)
    __slots__ = ['path']

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'component@{path}'.format(path=self.path)


class AppspaceQueue(object):

    appifies(AQueue)

    def __init__(self):
        self._queue = deque()

    def add_left(self, value):
        '''add item to left side of queue'''
        self._queue.appendleft(value)

    def pop_left(self):
        '''pop leftmost item in queue'''
        return self._queue.popleft()

    def add_right(self, value):
        '''add item to left side of queue'''
        self._queue.append(value)

    def pop_right(self):
        '''pop leftmost item in queue'''
        return self._queue.pop()
