# -*- coding: utf-8 -*-
'''appspace extension classes'''

from __future__ import absolute_import

from stuf.utils import setter

from appspace.keys import appifies

from .services import S
from .keys import AClient, AServer
from .containers import ResetMixin, Sync


class Host(ResetMixin):

    '''can have appspaced components attached'''


class Client(Host):

    '''consumes services from other instances'''

    appifies(AClient)

    def __init__(self):
        super(Client, self).__init__()
        # service tracker
        self._services = set()

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            # check for services
            if any([not key.startswith('__'), not key.upper()]):
                return setter(self, key, S(self).fetch(key))


class Server(Host):

    '''hosts services for other instances'''

    appifies(AServer)


class Synced(Host):

    '''instance with synchronizing functionality'''

    def __init__(self, element=None, **kw):
        '''
        init

        @param element: data to synchronize
        '''
        super(Synced, self).__init__()
        self._sync = Sync(element, **kw)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))


__all__ = ('Client', 'Host', 'Server', 'Synced')
