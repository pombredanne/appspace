# -*- coding: utf-8 -*-
'''appspace classes'''

from __future__ import absolute_import

#from collections import deque

from stuf.utils import either  # setter, lazy

#from appspace.utils import getcls
from appspace.keys import appifies

from .apps import __
from .keys import AClient, AServer
from .containers import ResetMixin, Sync


__all__ = ['Client', 'Host', 'Server', 'Synched']


class Base(ResetMixin):

    '''can have appspaced components attached'''

    # def __init__(self):
        #        for _, v in cls.Q.members(On):
#            v.__get__(None, cls)


class Client(Base):

    '''consumes services from other instances'''

    appifies(AClient)

    _services = set()

#    def __getattr__(self, key):
#        try:
#            return object.__getattribute__(self, key)
#        except AttributeError:
#            try:
#                query = __(self)
#                query.forwards()
#                value = query.pluck(key, self.F).one()
#                return setter(self, key, value)
#            except KeyError:
#                raise AttributeError('{0} not found'.format(key))


class Host(Base):

    '''hosts'''


class Server(Base):

    '''hosts services for other instances'''

    appifies(AServer)


class Synched(Server):

    '''delegate with synchronized class'''

    def __init__(self, original, **kw):
        super(Synched, self).__init__()
        self._sync = Sync(original, **kw)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))

    @either
    def C(self):
        '''local settings'''
        return __(self).localize().one()
