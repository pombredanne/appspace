# -*- coding: utf-8 -*-
'''service classes'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.keys import appifies
from appspace.query import ResetMixin

from .query import S
from .keys import AClient, AServer
from .core import forward, remote, service, servicer


class client(type):

    '''makes sure Traits are instantiated with their name attribute set'''

    def __new__(cls, name, bases, classdict):
        '''
        new

        instantiate Traits in classdict, setting their name attribute
        '''
        cls._servers = dict(
            (k, v) for k, v in classdict.iteritems()
            if isinstance(v, (forward, remote))
        )
        return super(client, cls).__new__(cls, name, bases, classdict)


@appifies(AClient)
class Client(ResetMixin):

    '''consumes services from other instances'''

    __metaclass__ = client

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            # check for services
            if any([not key.startswith('__'), not key.upper()]):
                return setattr(self, key, S(self).fetch(key))

    @lazy
    def _services(self):
        return set()


class server(type):

    '''makes sure Traits are instantiated with their name attribute set'''

    def __new__(cls, name, bases, classdict):
        '''
        new

        instantiate Traits in classdict, setting their name attribute
        '''
        cls._services = dict(
            (k, v) for k, v in classdict.iteritems()
            if isinstance(v, (servicer, service))
        )
        return super(server, cls).__new__(cls, name, bases, classdict)


@appifies(AServer)
class Server(ResetMixin):

    '''provides services for other instances'''

    __metaclass__ = server


__all__ = ('Client', 'Server')
