# -*- coding: utf-8 -*-
'''services classes'''

from __future__ import absolute_import

from stuf.utils import clsname, lazy, lazy_class

from appspace.query import Queried
from appspace.keys import appifies
from appspace import AppLookupError

from .queue import ServiceQueue
from .query import ServiceQuery
from .keys import AClient, AServer
from .decorators import forward, remote


class client(type):

    '''capture server names'''

    def __init__(cls, name, bases, classdict):
        # scan for servers
        items = (forward, remote)
        cls._servers = set(
            k for k, v in classdict.iteritems() if isinstance(v, items)
        )
        super(client, cls).__init__(name, bases, classdict)


@appifies(AClient)
class Client(Queried):

    '''consumes services from other instances'''

    __metaclass__ = client
    # key name
    _key_name = ''

    def __getattr__(self, key):
        try:
            return super(Client, self).__getattr__(key)
        except AttributeError:
            # lookup service in appspace
            if not key.startswith('__'):
                try:
                    return self._Q.get('.'.join([self._key, key]))
                # try resolving service
                except AppLookupError:
                    return self._SQ.resolve(key, self)
            else:
                raise AttributeError(key)

    @lazy_class
    def _SQ(self):
        # service query
        return ServiceQuery(self.A)

    @lazy_class
    def _SU(self):
        # service queue
        return ServiceQueue(self.A)

    @lazy
    def _key(self):
        # key
        return self._key_name if self._key_name else clsname(self)


@appifies(AServer)
class Server(Queried):

    '''provides services for other instances'''


__all__ = ('Client', 'Server')
