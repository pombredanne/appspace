# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''appspace management'''

from inspect import isclass
from operator import contains

from six import string_types
from appspace.keys import AppStore
from appspace.utils import lazy_import
from appspace.keys import AApp, ALazyApp, AManager, AppLookupError, appifies

__all__ = ('LazyApp', 'Manager')


@appifies(AManager)
class Manager(AppStore):

    '''state manager'''

    __slots__ = ('_key', '_label', '_ns')

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(Manager, self).__init__()
        self._label = label
        self._ns = ns
        self._key = AApp

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

        @param label: get or branch label
        '''
        key = self._key
        app = self.lookup1(key, key, label)
        if app is None:
            raise AppLookupError(app, label)
        if ALazyApp.providedBy(app):
            app = self.load(label, app.path)
        return app

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

    def load(self, label, module):
        '''
        load branch or get from appspace

        @param label: get or branch label
        @param module: module path
        '''
        # register branch appspace from include
        if isinstance(module, tuple):
            app = lazy_import(module[-1], self._label)
        # register get
        else:
            app = lazy_import(module)
        key = self._key
        self.register([key], key, label, app)
        return app

    def set(self, label, app):
        '''
        register branch or get in appspace

        @param label: appspace label
        @param get: get to add to appspace
        '''
        if isinstance(app, (string_types, tuple)):
            app = LazyApp(app)
        key = self._key
        self.register([key], key, label, app)
        return app


@appifies(ALazyApp)
class LazyApp(object):

    '''lazy get loader'''

    __slots__ = ['path']

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'app@{path}'.format(path=self.path)


iskeyed = Manager.iskeyed
