# -*- coding: utf-8 -*-
'''queues'''

from operator import getitem
from collections import deque


class NamedQueue(object):

    '''named queue'''

    __slots__ = ['_queue', 'max_length']

    def __init__(self, max_length=None):
        self._queue = deque(max_length) if max_length is not None else deque()
        self.max_length = max_length

    def __getitem__(self, key):
        for k, v in self:
            if k == key:
                return v
        else:
            raise KeyError('{key} not found'.format(key=key))

    def __iter__(self):
        for k, v in self._queue:
            yield [k, v]

    def __len__(self):
        return len(self._queue)

    def add_args_left(self, key, *args, **kw):
        '''
        add arguments to left side of queue

        @param key: key in queue
        '''
        self._queue.appendleft([key, (args, kw)])

    def add_args_right(self, key, *args, **kw):
        '''
        add arguments to right side of queue

        @param key: key in queue
        '''
        self._queue.append([key, (args, kw)])

    def add_left(self, key, value):
        '''
        dd item to left side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self._queue.appendleft([key, value])

    def add_right(self, key, value):
        '''
        add item to right side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self._queue.append([key, value])

    def clear(self):
        '''clear queue'''
        self._queue.clear()

    def get_left(self, key, default=None):
        '''
        get item by key from left side of queue

        @param key: key in queue
        @param default: default value (default: None)
        '''
        try:
            return getitem(self, key)
        except KeyError:
            return default

    def get_right(self, key, default=None):
        '''
        get item from right side of queue

        @param key: key in queue
        @param default: default vaue (default: None)
        '''
        self.reverse()
        try:
            value = getitem(self, key)
        except KeyError:
            value = default
        self.reverse()
        return value

    def pop_left(self):
        '''pop leftmost item in queue'''
        return self._queue.popleft()

    def pop_right(self):
        '''pop leftmost item in queue'''
        return self._queue.pop()

    def remove_left(self, key):
        '''
        remove item from left side of queue

        @param key: key in queue
        '''
        value = getitem(self, key)
        self._queue.remove(value)

    def remove_right(self, key):
        '''
        remove item from right side of queue

        @param key: key in queue
        '''
        self.reverse()
        value = getitem(self, key)
        self._queue.remove(value)
        self.reverse()

    def reverse(self):
        '''reverse queue order'''
        self._queue.reverse()

    def update_left(self, key, value):
        '''
        get item by key from left side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        for k in self._queue:
            if k[0] == key:
                key[1] = value
        else:
            raise KeyError('{key} not found'.format(key=key))

    def update_right(self, key, value):
        '''
        get item from right side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self.reverse()
        for k in self._queue:
            if k[0] == key:
                key[1] = value
        else:
            self.reverse()
            raise KeyError('{key} not found'.format(key=key))
        self.reverse()
