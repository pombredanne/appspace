# -*- coding: utf-8 -*-
'''query classes'''

from __future__ import absolute_import

from appspace.ext import ResetMixin

from stuf.utils import lazy

from appspace.keys import appifies

from .query import Q
from .conveyor import C
from .keys import AQueried, AQueued


@appifies(AQueried)
class Queried(ResetMixin):

    '''class supporting queries'''

    @lazy
    def _q(self):
        return Q(self)


@appifies(AQueued)
class Queued(ResetMixin):

    @lazy
    def _q(self):
        return C(self)

__all__ = ['Queued', 'Queried']
