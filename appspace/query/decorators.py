# -*- coding: utf-8 -*-
'''query decorators'''

from __future__ import absolute_import

from inspect import isclass

from .query import Q
from .builder import B


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
        return Q(that).get(self.label, self.branch).one()

    def __set__(self, this, value):
        raise AttributeError('attribute is read-only')

    def __delete__(self, this):
        raise AttributeError('attribute is read-only')


class factory(direct):

    '''builds application stored in appspace and passes it to host'''

    def __init__(self, label, branch=False, *args, **kw):
        '''
        init

        @param label: application label
        @param branch: branch label (default: False)
        '''
        super(factory, self).__init__(label, branch)
        self.attrs = args
        self.extra = kw

    def __get__(self, this, that):
        new_app = super(factory, self).__get__(this, that)
        if isclass(new_app):
            attrs = [getattr(this, attr) for attr in self.attrs]
            new_app = new_app(*attrs, **self.extra)
            B(that).set(new_app, self.label, self.branch)
        return new_app


__all__ = ('directory', 'factory')
