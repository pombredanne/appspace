# -*- coding: utf-8 -*-
'''service classes'''

from __future__ import absolute_import

from operator import attrgetter

from stuf.utils import lazy

from appspace.keys import appifies
from appspace.query import ResetMixin

from .query import S
from .keys import AClient, AServer
from .decorators import forward, remote


class client(type):

    '''capture server names'''

    def __init__(cls, name, bases, classdict):
        items = (forward, remote)
        cls._servers = set(
            k for k, v in classdict.iteritems() if isinstance(v, items)
        )
        super(client, cls).__init__(name, bases, classdict)


@appifies(AClient)
class Client(ResetMixin):

    '''consumes services from other instances'''

    __metaclass__ = client

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            # check for services
            query = self._query.service
            finder = attrgetter(key)
            for k in self._servers:
                try:
                    first = finder(getattr(self, k))
                    result = self.__dict__[key] = query(first).one()
                    return result
                except AttributeError:
                    pass
            else:
                raise AttributeError('{key}'.format(key=key))

    @lazy
    def _query(self):
        return S(self)


#class server(type):
#
#    '''capture services and names'''
#
#    def __init__(cls, name, bases, classdict):
#        items = (servicer, service)
#        cls._services = set(
#            k for k, v in classdict.iteritems() if isinstance(v, items)
#        )
#        super(server, cls).__init__(name, bases, classdict)


@appifies(AServer)
class Server(ResetMixin):

    '''provides services for other instances'''

#    __metaclass__ = server


__all__ = ('Client', 'Server')
