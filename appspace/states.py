# -*- coding: utf-8 -*-
'''appspace state management'''

from __future__ import absolute_import

from operator import contains

from stuf.utils import lazy

from .utils import lazy_import
from .events import EventManager
from .error import AppLookupError
from .settings import AppspaceSettings
from .core import (
    AppStore, AApp, AAppspaceManager, AEventManager, ALazyApp, ASettings,
    appifies)


class AppspaceManager(AppStore):

    '''state manager'''

    __slots__ = ['_label', '_settings', 'settings', 'events']

    appifies(AAppspaceManager)

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(AppspaceManager, self).__init__(())
        self._label = label
        self._settings = ns
        self._easy_register(ASettings, 'default', AppspaceSettings)
        self._easy_register(AEventManager, 'default', EventManager)

    def __contains__(self, label):
        return contains(self.names(((), AApp), label))

    def __repr__(self):
        return str(self.lookupAll((), AApp))

    @lazy
    def events(self):
        '''get events manager'''
        return self.easy_lookup(AEventManager, self._settings)(self)

    @lazy
    def settings(self):
        '''get settings'''
        return self.easy_lookup(ASettings, self._settings)()

    def easy_lookup(self, key, label):
        '''
        streamlined component lookup

        @param key: key to lookup
        @param label: label to lookup
        '''
        return self.lookup1(key, key, label)

    def easy_register(self, key, label, component):
        '''
        streamlined component registration

        @param key: key to register under
        @param label: label to register under
        @param component: component to register
        '''
        self.register([key], key, label, component)

    def easy_unregister(self, key, label):
        '''
        streamlined component unregistration

        @param key: key to lookup
        @param label: label to lookup
        '''
        self.unregister([key], key, label, self.easy_lookup(key, label))

    def get(self, label):
        '''
        fetch component

        @param label: component or branch label
        '''
        component = self.easy_lookup(AApp, label)
        if component is None:
            raise AppLookupError(component, label)
        if ALazyApp.providedBy(component):
            component = self.load(label, component.path)
        return component

    def load(self, label, module):
        '''
        load branch or component from appspace

        @param label: component or branch label
        @param module: Python module path
        '''
        # register branch appspace from include
        if isinstance(module, tuple):
            component = lazy_import(module[-1], self._label)
        # register component
        else:
            component = lazy_import(module)
        self.set(label, component)
        return component

    def set(self, label, component):
        '''
        register branch or component in appspace

        @param label: appspace label
        @param component: component to add to appspace
        '''
        if isinstance(component, (basestring, tuple)):
            component = LazyApp(component)
        self.register([AApp], AApp, label, component)


class LazyApp(object):

    '''lazy component loader'''

    __slots__ = ['path']

    appifies(ALazyApp)

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'component@{path}'.format(path=self.path)


# global appspace
global_appspace = AppspaceManager()
# global settings
global_settings = global_appspace.settings
