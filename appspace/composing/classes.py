# -*- coding: utf-8 -*-
'''composing classes'''

from __future__ import absolute_import

from operator import attrgetter

from stuf.utils import lazy, lazy_class

from appspace.keys import appifies
from appspace.building import Building

from .holders import Sync
from .query import ComposerQuery
from .queue import ComposerQueue
from .keys import AComposed, AMaster, ASynched


class ComposerMixin(Building):

    @lazy_class
    def _CQ(self):
        '''querier'''
        return ComposerQuery(self.A)

    @lazy_class
    def _CU(self):
        '''queuer'''
        return ComposerQueue(self.A)


@appifies(AComposed)
class Composed(ComposerMixin):

    '''composed object'''


@appifies(AMaster)
class Master(ComposerMixin):

    '''master composer'''


@appifies(ASynched)
class Synced(ComposerMixin):

    '''composed object with synchronizing functionality'''

    _element = attrgetter('element')
    _syncer = Sync

    def __getitem__(self, key):
        return self._sync.current[key]

    def __setitem__(self, key, value):
        return self._sync.update_current({key: value})

    def __delitem__(self, key):
        return self._sync.delete(key)

    def __contains__(self, key):
        return key in self._sync

    def __iter__(self):
        for k, v in self._sync:
            yield k, v

    def __repr__(self):
        return str(dict(i for i in self._sync.public.iteritems()))

    @lazy
    def _sync(self):
        # synchronizing handler
        return self._syncer(self._element(self), **self._attrs)


__all__ = ('Composed', 'Master', 'Synced')
