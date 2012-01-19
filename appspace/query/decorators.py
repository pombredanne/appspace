# -*- coding: utf-8 -*-
'''query decorators'''

from __future__ import absolute_import

from .query import Q
from stuf.utils import setter


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
        return setter(Q(that).get(self.label, self.branch))

    def __set__(self, this, value):
        raise AttributeError('attribute is read-only')

    def __delete__(self, this):
        raise AttributeError('attribute is read-only')


__all__ = ('direct')
