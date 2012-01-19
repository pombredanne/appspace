# -*- coding: utf-8 -*-
'''query classes'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.keys import appifies
from appspace.query import Queried, Queued

from .query import B
from .queue import BuildQueue
from .keys import ABuilt, ABuiltQueue


@appifies(ABuilt)
class Built(Queried):

    '''object that supports basic application building'''

    @lazy
    def _B(self):
        return B(self)


@appifies(ABuiltQueue)
class BuiltQueue(Queued):

    '''object that supports basic application building with a queue'''

    @lazy
    def _B(self):
        return BuildQueue(self)

__all__ = ['Queued', 'Queried']
