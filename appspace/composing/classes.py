# -*- coding: utf-8 -*-
'''composing classes'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.keys import appifies
from appspace.build import Built, BuiltQueue

from .query import __
from .mixin import SyncedMixin
from .queue import ComposerQueue
from .keys import AComposed, AComposedQueue


@appifies(AComposed)
class Composed(Built):

    '''composed object'''

    @lazy
    def _query(self):
        # query object
        return __(self)


@appifies(AComposedQueue)
class ComposedQueue(BuiltQueue):

    '''composed queue'''

    @lazy
    def _query(self):
        # query object
        return ComposerQueue(self)


class Synced(SyncedMixin, Composed):

    '''composed object with synchronizing functionality'''


class SyncedQueue(SyncedMixin, Composed):

    '''composed queue with synchronizing functionality'''


__all__ = ['Composed', 'ComposedQueue', 'Synced', 'SynchedQueue']
