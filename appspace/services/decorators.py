# -*- coding: utf-8 -*-
'''service decorators'''

from __future__ import absolute_import

from functools import wraps

from appspace.keys import apped
from appspace.query import direct
from appspace.building import factory

from .keys import AService


def service(*metadata):
    '''
    marks method as service

    @param *metadata: metadata to set on decorated method
    '''
    def wrapped(this):
        this.metadata = metadata

        @wraps(this)
        def wrapper(*args, **kw):
            return this(*args, **kw)
        apped(wrapper, AService)
        return wrapper
    return wrapped


class forward(factory):

    '''builds application in appspace and forwards host functionality to it'''


class remote(direct):

    '''makes remote functionality directly available to client'''


class servicer(factory):

    '''builds service and makes it available to clients'''


__all__ = ('forward', 'remote', 'service', 'servicer')
