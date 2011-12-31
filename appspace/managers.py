# -*- coding: utf-8 -*-
'''appspace management'''

from __future__ import absolute_import

from operator import contains

from stuf.utils import lazy

from .conf import Settings
from .utils import lazy_import
from .events import EventManager
from .error import AppLookupError
from .core import (
    AppStore, AApp, AManager, AEventManager, ALazyApp, ASettings, appifies)


class Manager(AppStore):

    '''state manager'''

    __slots__ = ['_label', '_settings', 'conf', 'events']

    appifies(AManager)

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(Manager, self).__init__(())
        self._label = label
        self._settings = ns
        self.easy_register(ASettings, 'default', Settings)
        self.easy_register(AEventManager, 'default', EventManager)

    def __contains__(self, label):
        return contains(self.names((), AApp), label)

    def __repr__(self):
        return str(self.lookupAll((), AApp))

    @lazy
    def events(self):
        '''get appspace events manager'''
        return self.easy_lookup(AEventManager, self._settings)(self)

    @lazy
    def conf(self):
        '''get appspace conf'''
        return self.easy_lookup(ASettings, self._settings)()

    def easy_lookup(self, key, label):
        '''
        streamlined app lookup

        @param key: key to lookup
        @param label: label to lookup
        '''
        return self.lookup1(key, key, label)

    def easy_register(self, key, label, app):
        '''
        streamlined app registration

        @param key: key to register
        @param label: label to register
        @param app: app to register
        '''
        self.register([key], key, label, app)

    def easy_unregister(self, key, label):
        '''
        streamlined app unregistration

        @param key: key to lookup
        @param label: label to lookup
        '''
        self.unregister([key], key, label, self.easy_lookup(key, label))

    def get(self, label):
        '''
        fetch app

        @param label: app or branch label
        '''
        app = self.easy_lookup(AApp, label)
        if app is None:
            raise AppLookupError(app, label)
        if ALazyApp.providedBy(app):
            app = self.load(label, app.path)
        return app

    def load(self, label, module):
        '''
        load branch or app from appspace

        @param label: app or branch label
        @param module: module path
        '''
        # register branch appspace from include
        if isinstance(module, tuple):
            app = lazy_import(module[-1], self._label)
        # register app
        else:
            app = lazy_import(module)
        self.set(label, app)
        return app

    def set(self, label, app):
        '''
        register branch or app in appspace

        @param label: appspace label
        @param app: app to add to appspace
        '''
        if isinstance(app, (basestring, tuple)):
            app = LazyApp(app)
        self.register([AApp], AApp, label, app)


class LazyApp(object):

    '''lazy app loader'''

    __slots__ = ['path']

    appifies(ALazyApp)

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'app@{path}'.format(path=self.path)


# global appspace
global_appspace = Manager()
# global conf
global_settings = global_appspace.settings
