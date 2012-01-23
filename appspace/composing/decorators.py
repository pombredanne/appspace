# -*- coding: utf-8 -*-
'''composing decorators'''

from __future__ import absolute_import

from functools import update_wrapper, wraps

from stuf.utils import selfname

from appspace.query.decorators import readonly


def on(*events):
    '''
    marks method as being a lazy instance

    @param *events: list of properties
    '''
    @wraps
    def wrapped(this):
        return On(this, *events)
    return wrapped


class On(readonly):

    '''attach events to method'''

    def __init__(self, method, *events):
        super(On, self).__init__()
        self.method = method
        self.events = events
        update_wrapper(self, method)

    def __get__(self, this, that):
        method = self.method
        ebind = that._CQ.manager.events.bind
        for arg in self.events:
            ebind(arg, method)
        setattr(that, selfname(method), method)
        return method


__all__ = ['on']
