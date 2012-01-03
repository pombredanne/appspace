# -*- coding: utf-8 -*-
'''appspace classes'''

from __future__ import absolute_import

from inspect import isclass
from functools import partial, wraps

from stuf.utils import getter, selfname, setter

from appspace.keys import appifies

from .apps import __
from .keys import AServer, AService

__all__ = ['service', 'on', 'remote', 'local']


def on(*events):
    '''
    marks method as being a lazy instance

    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


def service(*metadata):
    '''
    marks method as service

    @param *metadata: metadata to set on decorated method
    '''
    def wrapped(this):
        this.metadata = metadata
        __.key(AService, this)

        @wraps(this)
        def wrapper(*args, **kw):
            return this(*args, **kw)
        return wrapper
    return wrapped


class direct(object):

    '''passes application from appspace directly to host'''

    def __init__(self, label, branch=False):
        self.label = label
        self.branch = branch

    def __get__(self, this, that):
        return __(that).app(self.label, self.branch).one()

    def __set__(self, this, value):
        raise AttributeError('attribute is read-only')

    def __delete__(self, this):
        raise AttributeError('attribute is read-only')


class local(direct):

    '''builds application from appspace and passes it locally to host'''

    def __init__(self, label, branch=False, *args, **kw):
        super(local, self).__init__(label, branch)
        self.attrs = args
        self.extra = kw

    def __get__(self, this, that):
        new_app = super(local, self).__get__(this, that)
        if isclass(new_app):
            attrs = [getter(this, attr) for attr in self.attrs]
            new_app = new_app(*attrs, **self.extra)
            __(that).app(self.label, self.branch, new_app)
        return new_app


class remote(local):

    '''host delegates services to another class in appspace'''

    appifies(AServer)

    def __get__(self, this, that):
        new_app = super(remote, self).__get__(this, that)
        __(new_app).services(that, self.label, self.branch)
        return new_app


class Methodology(object):

    def __init__(self, method, *metadata):
        self.method = method
        self.metadata = metadata


class On(Methodology):

    '''attach events to method'''

    def __get__(self, this, that):
        ebind = __(that).manager.events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, selfname(method), method)


class Service(Methodology):

    '''method that can be delegated to another class'''

    def __get__(self, this, that):
        method = self.method
        kw = {}
        if self.metadata:
            kw.update(dict(
                (k, getter(that, k)) for k in self.metadata if hasattr(this, k)
            ))
        new_method = partial(method, this, **kw)
        return new_method
