# -*- coding: utf-8 -*-
'''composing decorators'''

from __future__ import absolute_import

from stuf.utils import selfname

from .query import __


def on(*events):
    '''
    marks method as being a lazy instance

    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class On(object):

    '''attach events to method'''

    def __init__(self, method, *metadata):
        self.method = method
        self.metadata = metadata

    def __get__(self, this, that):
        ebind = __(that).manager.events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        setattr(that, selfname(method), method)
        return method


__all__ = ['on']
