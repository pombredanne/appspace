# -*- coding: utf-8 -*-
'''extension services management'''

from __future__ import absolute_import

from stuf.utils import setter

from appspace.keys import appifies
from appspace.query import direct, factory

from .keys import AService, AServer


class ServiceMixin(object):

    def __get__(self, this, that):
        new_app = super(ServiceMixin, self).__get__(this, that)
#        S(new_app).scan(this, self.label)
        return setter(that, self.label, new_app)


@appifies(AServer)
class forward(ServiceMixin, factory):

    '''builds application in appspace and forwards host functionality to it'''


class remote(ServiceMixin, direct):

    '''makes remote functionality directly available to client'''


@appifies(AService)
class service(object):

    def __init__(self, method, *metadata):
        '''
        marks method as service

        @param *metadata: metadata to set on decorated method
        '''
        self.method = method
        self.method.metadata = metadata

    def __get__(self, this, that):
        return self.method


class servicer(factory):

    '''builds service and makes it available to clients'''

    def __get__(self, this, that):
        new_app = super(servicer, self).__get__(this, that)
#        S.key(AService, new_app)
        return setter(that, self.label, new_app)


__all__ = ('ServiceQuery', 'S', 'service')
