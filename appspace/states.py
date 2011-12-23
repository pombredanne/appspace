# -*- coding: utf-8 -*-
# pylint: disable-msg=w0232,e1001,e1002,f0401
'''state management'''

from __future__ import absolute_import

from operator import contains

from stuf.utils import lazy, getter, setter
from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry

from .error import AppLookupError
from .utils import lazy_import, tern
from .settings import AppspaceSettings
from .services import AppspaceQueue, LazyApp
from .events import AEvent, AEventHandler, EventHandler
from .keys import AApp, AAppspaceManager, ALazyApp, AQueue, ASettings


class AppspaceManager(AdapterRegistry):

    '''state manager'''

    __slots__ = ['_label', 'settings', '_settings']

    appifies(AAppspaceManager)

    def __init__(self, label='appconf', **kw):
        '''
        @param label: label for application configuration module
        '''
        super(AppspaceManager, self).__init__(())
        self._label = label
        self._queue = kw.pop('queue', 'default')
        self._settings = kw.pop('settings', 'default')
        self.register([ASettings], ASettings, 'default', AppspaceSettings)
        self.register([AQueue], AQueue, 'default', AppspaceQueue)
        self.register(
            [AEventHandler], AEventHandler, 'handler', EventHandler
        )

    def __contains__(self, label):
        return contains(self.names(((), AApp), label))

    def __repr__(self):
        return str(self.lookupAll((), AApp))

    @lazy
    def settings(self):
        '''get settings'''
        return self.lookup1(ASettings, ASettings, self._settings)()

    def bind(self, label, component):
        '''
        bind component to event

        @param event: event label
        @param component: object to bind to event
        '''
        self.subscribe([AApp], getter(self.get('handler'), label), component)

    def event(self, event):
        '''
        create new event

        @param event: event label
        '''
        class NewEvent(AEvent):
            '''event'''

        handler = self.get('handler')
        setter(handler, event, NewEvent)

    def get(self, label):
        '''
        fetch component

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
        component = tern(
            isinstance(module_path, tuple),
            # register branch appspace from include
            lazy_import(module_path[-1], self._label),
            # register component
            lazy_import(module_path),
        )
        self.set(label, component)
        return component

    def queue(self):
        '''queue'''
        return self.lookup1(AQueue, AQueue, self._queue)

    def react(self, label):
        '''
        returns objects bound to an event

        @param event: event label
        '''
        return self.subscribers(AApp, getter(self.get('handler'), label))

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
