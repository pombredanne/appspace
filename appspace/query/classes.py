# -*- coding: utf-8 -*-
'''queriable classes'''

from __future__ import absolute_import

from appspace.ext import ResetMixin

from stuf.utils import lazy

from appspace.keys import appifies

from .query import Q
from .queue import Queue
from .keys import AQueried, AQueued


@appifies(AQueried)
class Queried(ResetMixin):

    '''class supporting queries'''

    @lazy
    def _Q(self):
        return Q(self)


@appifies(AQueued)
class Queued(ResetMixin):

    @lazy
    def _Q(self):
        return Queue(self)

__all__ = ['Queued', 'Queried']
