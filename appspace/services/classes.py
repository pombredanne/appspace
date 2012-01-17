# -*- coding: utf-8 -*-
'''extension hosts'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.keys import appifies
from appspace.utils import ResetMixin

from .core import S
from .keys import AClient, AServer


@appifies(AClient)
class Client(ResetMixin):

    '''consumes services from other instances'''

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


@appifies(AServer)
class Server(ResetMixin):

    '''provides services for other instances'''


__all__ = ('Client', 'Server')
