# -*- coding: utf-8 -*-
'''query decorators'''

from __future__ import absolute_import

from functools import partial, update_wrapper

from stuf.utils import setter


class class_defer(object):

    def __init__(self, method):
        self.method = method
        update_wrapper(self, method)

    def __get__(self, this, that):
        method = self.method

        def function(*args, **kw):
            args = (that,) + args
            that._U.chain(partial(method, *args, **kw))
            return that
        update_wrapper(function, method)
        return function


class defer(object):

    def __init__(self, method):
        self.method = method
        update_wrapper(self, method)

    def __get__(self, this, that):
        method = self.method

        def function(*args, **kw):
            args = (this,) + args
            that._U.chain(partial(method, *args, **kw))
            return this
        update_wrapper(function, method)
        return function


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
        return setter(that, self.label, that._Q.get(self.label, self.branch))

    def __set__(self, this, value):
        raise AttributeError('attribute is read-only')

    def __delete__(self, this):
        raise AttributeError('attribute is read-only')


__all__ = ['direct']
