# -*- coding: utf-8 -*-
'''query decorators'''

from __future__ import absolute_import

from functools import partial, update_wrapper


class readonly(object):

    '''read-only descriptor'''

    def __set__(self, this, value):
        raise AttributeError('attribute is read-only')

    def __delete__(self, this):
        raise AttributeError('attribute is read-only')


class deferrable(readonly):

    '''deferred base class'''

    def __init__(self, method):
        '''
        defer method call

        @param method: method to defer
        '''
        super(deferrable, self).__init__()
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


class class_defer(deferrable):

    '''defer class method'''

    def __get__(self, this, that):
        # attach to class
        return self._factory(that)


class defer(deferrable):

    '''defer object method'''

    def __get__(self, this, that):
        # attach to objects
        return self._factory(this)


class direct(readonly):

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


__all__ = ['class_defer', 'defer', 'direct']
