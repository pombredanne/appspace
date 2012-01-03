# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''appspace management'''

from __future__ import absolute_import

from stuf.utils import lazy

from .utils import lazy_import
from .registry import Registry
from .settings import Settings
from .events import EventManager
from .keys import (
    AApp, AEventManager, ALazyApp, AManager, ASettings, appifies)


class Manager(Registry):

    '''state manager'''

    __slots__ = ['_label', '_key', '_settings', 'settings', 'events']

    appifies(AManager)

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(Manager, self).__init__(AApp, ns)
        self._label = label
        self.easy_register(ASettings, 'default', Settings)
        self.easy_register(AEventManager, 'default', EventManager)

    @lazy
    def events(self):
        '''get appspace events manager'''
        return self.easy_lookup(AEventManager, self._settings)(self)

    @lazy
    def settings(self):
        '''get appspace settings'''
        return self.easy_lookup(ASettings, self._settings)()

    def get(self, label):
        '''
        fetch app

        @param label: app or branch label
        '''
        app = super(Manager, self).get(label)
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
        super(Manager, self).set(label, app)


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
# global settings
global_settings = global_appspace.settings

__all__ = ['Manager', 'LazyApp', 'global_appspace', 'global_settings']
