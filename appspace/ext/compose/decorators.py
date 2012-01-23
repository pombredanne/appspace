# -*- coding: utf-8 -*-
'''composing decorators'''

from __future__ import absolute_import

from inspect import isclass
from functools import partial, update_wrapper, wraps

from stuf.utils import selfname


def on(*events):
    '''
    marks method as being a lazy instance

    @param *events: list of properties
    '''
    @wraps
    def wrapped(this):
        return _On(this, *events)
    return wrapped


class _readonly(object):

    '''read-only descriptor'''

    def __set__(self, this, value):
        raise AttributeError('attribute is read-only')

    def __delete__(self, this):
        raise AttributeError('attribute is read-only')


class _deferrable(_readonly):

    '''deferred base class'''

    def __init__(self, method):
        '''
        defer method call

        @param method: method to defer
        '''
        super(_deferrable, self).__init__()
        self.method = method

    def _factory(self, this):
        '''
        manufacture function

        @param this: this object
        '''
        method = self.method
        def function(*args, **kw): #@IgnorePep8
            # pack object reference into arguments
            args = (this,) + args
            # make partial
            this._U.chain(partial(method, *args, **kw))
            return this
        update_wrapper(function, method)
        return function


class class_defer(_deferrable):

    '''defer class method'''

    def __get__(self, this, that):
        # attach to class
        return self._factory(that)


class defer(_deferrable):

    '''defer object method'''

    def __get__(self, this, that):
        # attach to objects
        return self._factory(this)


class direct(_readonly):

    '''passes application from appspace directly to host'''

    def __init__(self, label, branch=False):
        '''
        init

        @param label: application label
        @param branch: branch label (default: False)
        '''
        super(direct, self).__init__()
        self.label = label
        self.branch = branch

    def __get__(self, this, that):
        app = that._Q.get(self.label, self.branch)
        setattr(that, self.label, app)
        return app


class factory(direct):

    '''
    builds application from factory stored in appspace and passes it to host
    '''

    def __init__(self, label, branch=False, *args, **kw):
        '''
        init

        @param label: application label
        @param branch: branch label (default: False)
        '''
        super(factory, self).__init__(label, branch)
        # method attributes
        self.attrs = args
        # method keywords
        self.extra = kw

    def __get__(self, this, that):
        label = self.label
        branch = self.branch
        # get app
        new_app = that._Q.get(label, branch)
        if isclass(new_app):
            # if factory build application
            new_app = new_app(
                *[getattr(this, attr) for attr in self.attrs], **self.extra
            )
            # set app
            that._B.set(new_app, label, branch)
        setattr(that, label, new_app)
        return new_app


class _On(_readonly):

    '''attach events to method'''

    def __init__(self, method, *events):
        super(_On, self).__init__()
        self.method = method
        self.events = events
        update_wrapper(self, method)

    def __get__(self, this, that):
        method = self.method
        ebind = that._C.manager.events.bind
        for arg in self.events:
            ebind(arg, method)
        setattr(that, selfname(method), method)
        return method


__all__ = ['class_defer', 'defer', 'direct', 'factory', 'on']
