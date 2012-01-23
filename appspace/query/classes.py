# -*- coding: utf-8 -*-
'''query classes'''

from __future__ import absolute_import

from stuf.utils import lazy_class

from appspace.keys import appifies
from appspace.ext import ResetMixin

from .queue import Queue
from .query import Query
from .keys import AQueried


@appifies(AQueried)
class Queried(ResetMixin):

    '''queriable object'''

    @lazy_class
    def _Q(self):
        '''querier'''
        return Query(self.A)

    @lazy_class
    def _U(self):
        '''queuer'''
        return Queue(self.A)


__all__ = ['Queried']
