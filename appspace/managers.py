# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''application management'''

from __future__ import absolute_import

from .utils import lazy_import
from .registry import Registry

from .error import AppLookupError
from .keys import AApp, ALazyApp, AManager, appifies


@appifies(AManager)
class Manager(Registry):

    '''state manager'''

    __slots__ = ('_key', '_label', '_manager', '_settings')

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(Manager, self).__init__(AApp, ns)
        self._label = label
        self._manager = None

    @property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, manager):
        self.register([AManager], AManager, 'manager', manager)

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
        if isinstance(app, (basestring, tuple)):
            app = LazyApp(app)
        key = self._key
        self.register([key], key, label, app)


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


__all__ = ('Manager', 'LazyApp')
