# -*- coding: utf-8 -*-
'''appspace classes'''

from __future__ import absolute_import

from stuf.utils import either, setter

from appspace.utils import getcls
from appspace.core import appifies

from .query import __
from .core import AClient, AServer
from .containers import ResetMixin, Sync


__all__ = ['Server', 'Client', 'Synched']


class Base(ResetMixin):

    '''can have appspaced components attached'''

    def __new__(cls, *args, **kw):
#        for _, v in cls.Q.members(On):
#            v.__get__(None, cls)
        new = super(Base, cls).__new__
        # needed because Python 2.6 object.__new__ only accepts cls argument
        if new == object.__new__:
            return new(cls)
        return new(cls, *args, **kw)

    @either
    def C(self):
        '''local settings'''
        return __(self).localize().one()


class Server(Base):

    '''hosts services for other instances'''

    appifies(AServer)


class Client(Base):

    '''consumes services from other instances'''

    appifies(AClient)

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            try:
                return setter(
                    getcls(self), key, __(self).pluck(key, self.D).first()
                )
            except KeyError:
                raise AttributeError('{0} not found'.format(key))


class Synched(Server):

    '''delegate with synchronized class'''

    def __init__(self, original, **kw):
        super(Synched, self).__init__()
        self._sync = Sync(original, **kw)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))
