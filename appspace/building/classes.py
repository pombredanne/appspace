# -*- coding: utf-8 -*-
'''building classes'''

from __future__ import absolute_import

from stuf.utils import lazy_class

from appspace.query import Queried
from appspace.keys import appifies

from .keys import ABuilding
from .query import BuildQuery
from .queue import BuildQueue


@appifies(ABuilding)
class Building(Queried):

    '''building object'''

    @lazy_class
    def _BQ(self):
        '''querier'''
        return BuildQuery(self.A)

    @lazy_class
    def _BU(self):
        '''queuer'''
        return BuildQueue(self.A)


__all__ = ['Building']
