# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''application management'''

from __future__ import absolute_import

from operator import contains

from .keys import AppStore
from .error import AppLookupError


class Registry(AppStore):

    __slots__ = ('_key', '_settings')

    def __init__(self, key, ns='default'):
        '''
        init

        @param ns: label for internal namespace
        '''
        super(Registry, self).__init__(())
        self._settings = ns
        self._key = key

    def __contains__(self, label):
        return contains(self.names([self._key], self._key), label)

    def __repr__(self):
        return str(self.lookupAll([self._key], self._key))

    def ez_lookup(self, key, label):
        '''
        streamlined get lookup

        @param key: key to lookup
        @param label: label to lookup
        '''
        return self.lookup1(key, key, label)

    def ez_register(self, key, label, app):
        '''
        streamlined get registration

        @param key: key to register
        @param label: label to register
        @param app: app to register
        '''
        self.register([key], key, label, app)

    def ez_unregister(self, key, label):
        '''
        streamlined get unregistration

        @param key: key to lookup
        @param label: label to lookup
        '''
        self.unregister([key], key, label, self.ez_lookup(key, label))

    def get(self, label):
        '''
        fetch app

        @param label: app or branch label
        '''
        app = self.ez_lookup(self._key, label)
        if app is None:
            raise AppLookupError(app, label)
        return app

    def set(self, label, app):
        '''
        register branch or app in appspace

        @param label: appspace label
        @param app: app to add to appspace
        '''
        self.register([self._key], self._key, label, app)


__all__ = ['Registry']
