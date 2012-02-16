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
        streamlined app lookup

        @param key: key to lookup
        @param label: label to lookup
        '''
        return self.lookup1(key, key, label)

    def ez_register(self, key, label, app):
        '''
        streamlined app registration

        @param key: key to register
        @param label: label to register
        @param app: app to register
        '''
        self.register([key], key, label, app)

    def ez_subscribe(self, key, label, app):
        '''
        streamlined app subscription

        @param key: key to extend to
        @param label: label to extend to
        '''
        self.extend(key, self.key(key, label), app)

    def ez_unregister(self, key, label):
        '''
        streamlined app unregistration

        @param key: key to lookup
        @param label: label to lookup
        '''
        self.unregister([key], key, label, self.ez_lookup(key, label))

    unkey = ez_unregister

    def ez_unsubscribe(self, key, label):
        '''
        streamlined app unsubscription

        @param key: key to lookup
        @param label: label to lookup
        '''
        self.unsubscribe(key, self.ez_lookup(key, label))

    def key(self, key, label):
        '''
        create or fetch key

        @param key: key to register
        @param label: label to register
        '''
        this = self.lookup1(key, key, label)
        if this is None:
            this = self.create()
            self.register([key], key, label, this)
        return this

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
    def create(cls):
        '''create new key'''
        return InterfaceClass(cls.uuid())

    @staticmethod
    def uuid():
        '''universal unique identifier'''
        return uuid.uuid4().hex.upper()
