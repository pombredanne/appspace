# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001
'''appspace registry'''

import uuid
import hashlib
from inspect import isclass
from operator import contains

from appspace.six import u
from appspace.keys import AppStore, InterfaceClass

__all__ = ['Registry']


class Registry(AppStore):

    '''app registry'''

    __slots__ = ('_key', '_label', '_ns')

    def __init__(self, label='appconf', ns='default', key=None):
        '''
        init

        @param label: label for appconf (default: 'appconf')
        @param ns: label for internal namespace (default: 'default')
        @param key: registry key (default: None)
        '''
        super(Registry, self).__init__()
        self._label = label
        self._ns = ns
        self._key = key

    def __contains__(self, label):
        return contains(self.names([self._key], self._key), label)

    def __repr__(self):
        return str(self.lookupAll([self._key], self._key))

    @staticmethod
    def ez_id(this):
        '''easy unique identifier for an object'''
        return hashlib.sha1(u(id(this))).digest()

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

    @staticmethod
    def iskeyed(key, this):
        '''
        check if item has an app key

        @param label: app key
        @param this: object to check
        '''
        try:
            if isclass(this):
                return key.implementedBy(this)
            return key.providedBy(this)
        except AttributeError:
            return False

    @classmethod
    def key(cls):
        '''random interface'''
        return InterfaceClass(cls.uuid())

    @staticmethod
    def uuid():
        '''universal unique identifier'''
        return uuid.uuid4().hex.upper()
