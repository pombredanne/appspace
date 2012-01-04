# -*- coding: utf-8 -*-
'''appspace extensions classes'''

from __future__ import absolute_import

from stuf.utils import either, setter

from appspace.keys import appifies

from .apps import __
from .services import S
from .keys import AClient, AServer
from .containers import ResetMixin, Sync


class Host(ResetMixin):

    '''can have appspaced components attached'''


class Client(Host):

    '''consumes services from other instances'''

    appifies(AClient)

    _services = set()

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if any([not key.startswith('__'), not key.upper()]):
                return setter(self, key, S(self).fetch(key))


class Master(Host):

    '''master class'''


class Server(Host):

    '''hosts services for other instances'''

    appifies(AServer)


class Synched(Host):

    '''delegate with synchronized class'''

    def __init__(self, original, **kw):
        super(Synched, self).__init__()
        self._sync = Sync(original, **kw)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))

    @either
    def C(self):
        '''local settings'''
        return __(self).localize().one()


__all__ = ('Client', 'Host', 'Master', 'Server', 'Synched')
