# -*- coding: utf-8 -*-
'''named queue'''

from operator import getitem
from collections import deque


class namedqueue(deque):

    '''named queue'''

    def __init__(self, max_length=None, *args):
        deque.__init__(self, maxlen=max_length, *args)

    def __getitem__(self, key):
        try:
            return deque.__getitem__(self, key)
        except IndexError:
            for k in self:
                try:
                    if k[0] == key:
                        return k[1]
                except IndexError:
                    pass
            else:
                raise KeyError(key)

    def add_args_left(self, key, *args, **kw):
        '''
        add arguments to left side of queue

        @param key: key in queue
        '''
        self.appendleft([key, (args, kw)])

    def add_args_right(self, key, *args, **kw):
        '''
        add arguments to right side of queue

        @param key: key in queue
        '''
        self.append([key, (args, kw)])

    def add_left(self, key, value):
        '''
        add item to left side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self.appendleft([key, value])

    def add_right(self, key, value):
        '''
        add item to right side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        self.append([key, value])

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

    def iteritems(self):
        for k in self:
            try:
                yield k[0], k[1]
            except ValueError:
                pass

    def remove_left(self, key):
        '''
        remove item from left side of queue

        @param key: key in queue
        '''
        value = getitem(self, key)
        self.remove(value)

    def remove_right(self, key):
        '''
        remove item from right side of queue

        @param key: key in queue
        '''
        self.reverse()
        value = getitem(self, key)
        self.remove(value)
        self.reverse()

    def update_left(self, key, value):
        '''
        get item by key from left side of queue

        @param key: key in queue
        @param value: value to put in queue
        '''
        for k in self:
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
        for k in self:
            if k[0] == key:
                key[1] = value
        else:
            self.reverse()
            raise KeyError('{key} not found'.format(key=key))
        self.reverse()
