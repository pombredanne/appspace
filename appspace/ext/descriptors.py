# -*- coding: utf-8 -*-
'''appspace classes'''

from __future__ import absolute_import

from inspect import isclass

from stuf.utils import getter

from appspace.keys import appifies

from .apps import __
from .services import S
from .keys import AServer


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


class remote(direct):

    '''host delegates functionality to application from appspace'''

    appifies(AServer)

    def __get__(self, this, that):
        new_app = super(remote, self).__get__(this, that)
        S(new_app).scan(that, self.label)
        return new_app


class factory(direct):

    '''builds application stored in appspace and passes it to host'''

    def __init__(self, label, branch=False, *args, **kw):
        super(factory, self).__init__(label, branch)
        self.attrs = args
        self.extra = kw

    def __get__(self, this, that):
        new_app = super(factory, self).__get__(this, that)
        if isclass(new_app):
            attrs = [getter(this, attr) for attr in self.attrs]
            new_app = new_app(*attrs, **self.extra)
            __(that).app(self.label, self.branch, new_app)
        return new_app


class forward(remote, factory):

    '''builds application in appspace and forwards host functionality to it'''


__all__ = ['direct', 'factory', 'forward', 'remote']
