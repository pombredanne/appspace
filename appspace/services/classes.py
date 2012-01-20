# -*- coding: utf-8 -*-
'''service classes'''

from __future__ import absolute_import

from stuf.utils import clsname, lazy

from appspace.keys import appifies
from appspace import AppLookupError
from appspace.ext.classes import ResetMixin

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
class Client(ResetMixin):

    '''consumes services from other instances'''

    __metaclass__ = client
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
                    return self._S.resolve(key, self)
            else:
                raise AttributeError(key)

    @lazy
    def _key(self):
        # key
        return self._key_name if self._key_name else clsname(self)


@appifies(AServer)
class Server(ResetMixin):

    '''provides services for other instances'''


__all__ = ('Client', 'Server')
