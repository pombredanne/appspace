# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,e1002,f0401,e1101,e1001
'''appspace state management'''

from __future__ import absolute_import
from collections import deque, namedtuple

from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry

from .error import AppLookupError
from .util import lazy_import, lazy
from .keys import AAppspaceManager, AAppSettings, AAppQueue, AApp, ALazyApp


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
            [AAppSettings], AAppSettings, 'default', AppspaceSettings
        )
        self.register([AAppQueue], AAppQueue, 'default', AppspaceQueue)

    def __contains__(self, label):
        return label in self.names((), AApp)

    def __repr__(self):
        return str(self.lookupAll((), AApp))

    @lazy
    def queue(self):
        '''appspace queue'''
        return self.lookup1(AAppQueue, AAppQueue, self._queue)

    @lazy
    def settings(self):
        '''appspace settings'''
        return self.lookup1(AAppSettings, AAppSettings, self._settings)

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
        if isinstance(component, LazyApp):
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


class AppspaceSettings(object):

    '''appspace settings'''

    appifies(AAppSettings)

    def __init__(self, **kw):
        self._main = dict(**kw)
        self._default = {}
        self._internal = {}

    @property
    def default(self):
        '''transform dict into named tuple'''
        return self.freeze('default', self._default)

    @property
    def internal(self):
        '''transform dict into named tuple'''
        return self.freeze('internal', self._default)

    @property
    def public(self):
        '''transform dict into named tuple'''
        main = self._default.copy()
        main.update(self._main.copy())
        return self.freeze('public', main)

    def freeze(self, name, settings):
        '''transform dict into named tuple'''
        frozen = namedtuple(name, settings.keys(), rename=True)
        return frozen(**settings.items())

    def get(self, key, default=None, namespace=None):
        if default is None:
            default = self._default.get(key)
        if namespace:
            return self._main.get(namespace, {}).get(key, default)
        return self._main.get(key, default)

    def get_internal(self, key):
        return self._default.get(key)

    def set(self, key, value, namespace=None):
        if namespace is not None:
            nspace = self._main.setdefault(namespace, dict(key=value))
            nspace[key] = value
        else:
            self._main[key] = value

    def set_default(self, key, value):
        self._default[key] = value

    def set_internal(self, key, value):
        self._internal[key] = value

    def update_default(self, *args, **kw):
        self._default.update(*args, **kw)

    def update_internal(self, *args, **kw):
        self._internal.update(*args, **kw)

    def update_settings(self, *args, **kw):
        self._main.update(*args, **kw)


class AppspaceQueue():

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
