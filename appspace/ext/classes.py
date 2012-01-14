# -*- coding: utf-8 -*-
'''appspace extension classes'''

from __future__ import absolute_import

from operator import attrgetter

from stuf.utils import lazy, setter

from appspace.keys import appifies
from appspace.utils import ResetMixin

from .services import S
from .holders import Sync
from .keys import AClient, AServer, ASynched


@appifies(AClient)
class Client(ResetMixin):

    '''consumes services from other instances'''

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            # check for services
            if any([not key.startswith('__'), not key.upper()]):
                return setter(self, key, S(self).fetch(key))

    @lazy
    def _services(self):
        return set()


@appifies(AServer)
class Server(ResetMixin):

    '''provides services for other instances'''


@appifies(ASynched)
class Synced(ResetMixin):

    '''instance with synchronizing functionality'''

    _element = attrgetter('element')
    _syncer = Sync

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))

    @lazy
    def _sync(self):
        return self._syncer(self._element(self), **self._attrs)


__all__ = ('Client', 'Server', 'Synced')
