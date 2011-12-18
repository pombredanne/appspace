# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,e1002,f0401,e1101,e1001
'''appspace state management'''

from __future__ import absolute_import
from collections import deque

from stuf import frozenstuf
from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry
from stuf.utils import object_lookup, lazy_set, lazy

from .error import AppLookupError
from .utils import ResetMixin, lazy_import, object_walk
from .keys import (
    AAppspaceManager, ASettings, AQueue, AApp, ALazyApp, AInternalSettings,
    ADefaultSettings,
)


class LazyApp(object):

    '''lazy component loader'''

    __slots__ = ['path']

    appifies(ALazyApp)

    def __init__(self, path):
        '''
        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'App@{path}'.format(path=self.path)


class AppspaceManager(AdapterRegistry):

    '''appspace state manager'''

    __slots__ = ['_label', 'settings', '_settings', 'queue', '_queue']

    appifies(AAppspaceManager)

    def __init__(self, label='appconf', bases=(), **kw):
        '''
        @param label: label for application module name
        '''
        super(AppspaceManager, self).__init__(bases)
        self._label = label
        self._queue = kw.pop('queue', 'default')
        self._settings = kw.pop('settings', 'default')
        self.register(
            [ASettings], ASettings, 'default', AppspaceSettings
        )
        self.register([AQueue], AQueue, 'default', AppspaceQueue)

    def __contains__(self, label):
        return label in self.names((), AApp)

    def __repr__(self):
        return str(self.lookupAll((), AApp))

    @lazy
    def queue(self):
        '''appspace queue'''
        return self.lookup1(AQueue, AQueue, self._queue)

    @lazy
    def s(self):
        return self.settings

    @lazy
    def settings(self):
        '''appspace settings'''
        return self.lookup1(ASettings, ASettings, self._settings)

    def _component(self, label, module_path):
        '''
        register branch appspaces or apps in appspace

        @param label: component or branch appspace
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

    def get(self, label):
        '''
        component fetcher

        @param appkey: application key
        @param label: component or branch appspace name
        '''
        component = self.lookup1(AApp, AApp, label)
        if component is None:
            raise AppLookupError(component, label)
        if ALazyApp.providedBy(component):
            component = self._component(label, component.path)
        return component

    def set(self, label, component):
        '''
        register component

        @param component: component to add to appspace
        @param label: appspace name
        '''
        if isinstance(component, (basestring, tuple)):
            component = LazyApp(component)
        self.register([AApp], AApp, label, component)


class AppspaceSettings(ResetMixin):

    '''appspace settings'''

    appifies(ASettings)

    def __init__(self, **kw):
        super(AppspaceSettings, self).__init__()
        self._main = dict(**kw)
        self._default = {}
        self._internal = {}

    @lazy_set
    def default(self):
        '''get default settings separately'''
        return frozenstuf(self._default)

    @default.setter
    def default(self, value):
        '''
        set default settings separately

        @param value: default settings
        '''
        if ADefaultSettings.implementedBy(value):
            self._default.clear()
            self.update_default(value)
        else:
            raise TypeError('invalid DefaultSettings')

    @lazy_set
    def internal(self):
        '''get internal settings separately'''
        return frozenstuf(self._default)

    @internal.setter
    def internal(self, value):
        '''
        set internal settings separately

        @param value: internal settings
        '''
        if AInternalSettings.implementedBy(value):
            self._internal.clear()
            self.update_internal(value)
        else:
            raise TypeError('invalid InternalSettings')

    @lazy
    def main(self):
        '''get main settings separately'''
        main = self._default.copy()
        main.update(self._main.copy())
        main.update(self._internal.copy())
        return frozenstuf(main)

    def get(self, key, namespace=None, appspace=None, default=None):
        if default is None:
            default = self._default.get(key)
        if namespace:
            return self._main.get(namespace, {}).get(key, default)
        return self._main.get(key, default)

    def set(self, key, value, namespace=None):
        if namespace is not None:
            nspace = self._main.setdefault(namespace, dict(key=value))
            nspace[key] = value
        else:
            self._main[key] = value

    def lookup(self, setting):
        try:
            setting = setting.split('.')
        except AttributeError:
            pass
        return object_lookup(setting, self.main)

    def update_default(self, settings):
        if ADefaultSettings.implementedBy(settings):
            self.reset()
            self._default.update(object_walk(settings))
        else:
            raise TypeError('invalid DefaultSettings')

    def update_internal(self, settings):
        if AInternalSettings.implementedBy(settings):
            self.reset()
            self._internal.update(object_walk(settings))
        else:
            raise TypeError('invalid InternalSettings')

    def update(self, *args, **kw):
        self._main.update(*args, **kw)


class AppspaceQueue(object):

    def __init__(self):
        self._queue = deque()

    def add_left(self, value):
        '''add item to left side of queue'''
        self._queue.appendleft(value)

    def pop_left(self):
        '''pop leftmost item in queue'''
        return self._queue.popleft()

    def add_right(self, value):
        '''add item to left side of queue'''
        self._queue.append(value)

    def pop_right(self):
        '''pop leftmost item in queue'''
        return self._queue.pop()


# global appspace
global_appspace = AppspaceManager()

# global settings
global_settings = global_appspace.settings
