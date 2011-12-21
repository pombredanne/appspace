# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002,f0401
'''state management'''

from __future__ import absolute_import
from operator import contains

from stuf.utils import lazy
from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry

from .utils import lazy_import
from .error import AppLookupError
from .settings import AppspaceSettings
from .services import AppspaceQueue, LazyApp
from .keys import AApp, AAppspaceManager, ALazyApp, AQueue, ASettings


class AppspaceManager(AdapterRegistry):

    '''state manager'''

    __slots__ = ['_label', 'queue', '_queue', 'settings', '_settings']

    appifies(AAppspaceManager)

    def __init__(self, label='appconf', bases=(), **kw):
        '''
        @param label: label for application configuration module
        '''
        super(AppspaceManager, self).__init__(bases)
        self._label = label
        self._queue = kw.pop('queue', 'default')
        self._settings = kw.pop('settings', 'default')
        self.register([ASettings], ASettings, 'default', AppspaceSettings)
        self.register([AQueue], AQueue, 'default', AppspaceQueue)

    def __contains__(self, label):
        return contains(self.names((), AApp), label)

    def __repr__(self):
        return str(self.lookupAll((), AApp))

    @lazy
    def queue(self):
        '''appspace queue'''
        return self.lookup1(AQueue, AQueue, self._queue)()

    @lazy
    def settings(self):
        '''appspace settings'''
        return self.lookup1(ASettings, ASettings, self._settings)()

    def bind(self, event, this):
        first, second = self.get(event)()
        self.subscribe(first, second, this)

    def react(self, event):
        first, second = self.get(event)()
        return self.subscribers(first, second)

    def get(self, label):
        '''
        component fetcher

        @param label: component or branch label
        '''
        component = self.lookup1(AApp, AApp, label)
        if component is None:
            raise AppLookupError(component, label)
        if ALazyApp.providedBy(component):
            component = self.load(label, component.path)
        return component

    def load(self, label, module_path):
        '''
        load branch or component from appspace

        @param label: component or branch label
        @param module_path: Python module path
        '''
        # register branch appspace from included module
        if isinstance(module_path, tuple):
            component = lazy_import(module_path[-1], self._label)
        # register component
        else:
            component = lazy_import(module_path)
        self.set(label, component)
        return component

    def set(self, label, component):
        '''
        register branches or components in appspace

        @param label: appspace label
        @param component: component to add to appspace
        '''
        if isinstance(component, (basestring, tuple)):
            component = LazyApp(component)
        self.register([AApp], AApp, label, component)


# global appspace
global_appspace = AppspaceManager()
# global settings
global_settings = global_appspace.settings
