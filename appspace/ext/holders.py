# -*- coding: utf-8 -*-
'''appspace collections'''

import hashlib
from operator import getitem
from collections import deque

from stuf import stuf
from stuf.utils import lazy


class DictDiff(object):

    '''
    calculate the difference between two dictionaries as:

    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values

    originally derived from example from 'hughdbrown':

    http://stackoverflow.com/questions/1165352/
    fast-comparison-between-two-python-dictionary
    '''

    def __init__(self, current, past):
        self.current = current
        self.past = past
        self.set_current = set(current.keys())
        self.set_past = set(past.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    @lazy
    def added(self):
        '''added changes'''
        return self.set_current - self.intersect

    @lazy
    def changed(self):
        '''changed data'''
        return {
            o for o in self.intersect if self.past[o] != self.current[o]
        }

    @lazy
    def future_diff(self):
        '''future changes'''
        return stuf({
            k: v for k, v in self.current.iteritems() if k in self.changed
        })

    @lazy
    def past_diff(self):
        '''past changes'''
        return stuf({
            k: v for k, v in self.past.iteritems() if k in self.changed
        })

    @lazy
    def removed(self):
        '''removed changes'''
        return self.set_past - self.intersect

    @lazy
    def unchanged(self):
        '''unchanged data'''
        return {
            o for o in self.intersect if self.past[o] == self.current[o]
        }


class namedqueue(object):

    '''named queue'''

    __slots__ = ('_queue', 'max_length')

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

    def __repr__(self):
        return str(self._queue)

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
        add item to left side of queue

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


class Sync(object):

    '''synchronizing class'''

    def __init__(self, original=None, **kw):
        '''
        init

        @param original: original data
        @param **kw: any updated data
        '''
        super(Sync, self).__init__()
        # add original
        self.original = stuf(original) if original is not None else stuf()
        # build current from original
        self.current = stuf(original.copy()) if original else stuf()
        if kw:
            # preserve changed data as reference
            self.changed = stuf(kw)
            # add changed data to current data
            self.current.update(self.changed)
            # set modified flat to True
            self.modified = True
        else:
            # empty change reference
            self.changed = stuf()
            # modified flag is False
            self.modified = False
        # dictionary for cleaned data
        self.cleaned = stuf()

    def __call__(self):
        '''get cleaned data'''
        return self.cleaned

    def __contains__(self, key):
        # check if key is in current
        return key in self.current

    def __iter__(self):
        for k, v in self.current.iteritems():
            yield k, v

    def __repr__(self):
        return unicode(dict(iter(self)))

    @property
    def private(self):
        '''private data (key starts with '_')'''
        return stuf(
            (k, v) for k, v in self.current.iteritems() if k.startswith('_')
        )

    @property
    def properties(self):
        '''all public and private data'''
        return stuf(self.current.copy())

    @property
    def public(self):
        '''public data (key does not start with '_')'''
        return stuf(
            (k, v) for k, v in self.current.iteritems()
            if not k.startswith('_')
        )

    def commit(self):
        '''commit all current changes'''
        # update original with current data
        self.update_original(self.current)
        # update cleaned data
        self.cleaned.update(self.current.copy())
        # clear changes
        self.changed.clear()
        # mark as unmodified
        self.modified = False

    def copy(self, **kw):
        '''make a copy and update with any keyword arguments'''
        previous = stuf(i for i in self)
        previous.update(kw)
        return previous

    def diff(self):
        '''diff between current and original version'''
        return DictDiff(self.current, self.original).future_diff

    def diff_hash(self):
        '''hash of diff between current data and updated data'''
        return hashlib.sha512(str(self.diff())).hexdigest()

    def hash(self):
        '''hash of current data'''
        return hashlib.sha512(str(self.current)).hexdigest()

    def rollback(self):
        '''rollback all changes'''
        # drop changes
        self.changed.clear()
        # reset
        self.reset()
        # flag as unmodified
        self.modified = False

    def reset(self):
        '''
        reset current data

        @param kw: keyword arguments
        '''
        # reset current
        self.current.clear()
        self.current.update(self.original.copy() if self.original else stuf())
        # drop cleaned
        self.cleaned.clear()

    def update_current(self, kw):
        '''
        update current data

        @param kw: keyword arguments
        '''
        # update current
        self.current.update(kw)
        # update changed data reference
        self.changed.update(kw)
        # clear any cleaned data
        self.cleaned.clear()
        # flag as modified
        self.modified = True

    def update_original(self, kw):
        '''
        update original data

        @param kw: keyword arguments
        '''
        self.original.update(kw)
        self.reset()


__all__ = ('Sync', 'namedqueue')
