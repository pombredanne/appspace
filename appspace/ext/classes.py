# -*- coding: utf-8 -*-
'''appspace classes'''

from __future__ import absolute_import

from functools import partial, update_wrapper

from stuf.utils import getter, selfname, either, setter

from appspace.utils import getcls
from appspace.core import appifies

from .query import __
from .core import ADelegater, ADelegate
from .containers import ResetMixin, Sync


__all__ = ['delegate', 'on', 'Delegate', 'Delegater', 'Synched']


def delegate(*metadata):
    '''
    marks method as delegate

    @param *metadata: metadata to set on decorated method
    '''
    def wrapped(func):
        return Delegatee(func, *metadata)
    return wrapped


def on(*events):
    '''
    marks method as being a lazy instance

    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


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
        '''local appspaced settings'''
        return __(self).localize().one()


class Methodology(object):

    def __init__(self, method, *metadata):
        self.method = method
        self.metadata = metadata
        update_wrapper(self, method)


class Delegatee(Methodology):

    '''method that can be delegated to another class'''

    def __get__(self, this, that):
        method = self.method
        if self.metadata:
            kw = dict(
                (k, getter(that, k)) for k in self.metadata if hasattr(this, k)
            )
            if kw:
                method = update_wrapper(partial(method, **kw), method)
        return method


class On(Methodology):

    '''attach events to method'''

    def __get__(self, this, that):
        ebind = __(that).manager.events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, selfname(method), method)


class Delegate(Base):

    '''can have attributes and methods delegated to it'''

    appifies(ADelegate)


class Delegater(Base):

    '''can delegate attributes and methods to appspaced components'''

    appifies(ADelegater)

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


class Synched(Delegate):

    '''delegate with synchronized class'''

    def __init__(self, original, **kw):
        super(Synched, self).__init__()
        self._sync = Sync(original, **kw)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))
