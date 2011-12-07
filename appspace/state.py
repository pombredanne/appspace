# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232
'''appspace state management'''

from importlib import import_module

## pylint: disable-msg=f0401
from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry
## pylint: disable-msg=f0401

from appspace.util import lru_cache
from appspace.error import AppLookupError 
from appspace.keys import AAppspaceManager, AApp


class App(object):
    
    appifies(AApp)
    
    def __init__(self, path):
        self.path = path


class AppspaceManager(AdapterRegistry):

    '''appspace state manager'''

    __slots__ = ['_apps']

    appifies(AAppspaceManager)

    def __init__(self):
        super(AppspaceManager, self).__init__()
        
    def _app(self, name, path):
        '''
        register appspaces or apps in appspace

        @param name: app or appspace
        @param path: Python path
        '''
        # register branch appspace from included module
        if isinstance(path, tuple):
            app = getattr(self._load('.'.join([path[-1], 'apps'])), 'apps')
        # register app
        else:
            app = self._load(path)
        self.set(app, AApp, name)
        return app
        
    def _load(self, path):
        '''
        dynamic loader

        @param path: something to load
        '''
        if isinstance(path, str):
            try:
                dot = path.rindex('.')
                # import module
                path = getattr(import_module(path[:dot]), path[dot+1:])
            # If nothing but module name, import the module
            except AttributeError:
                path = import_module(path)
        return path

    @lru_cache()
    def get(self, app, name=''):
        '''app fetcher'''
        app = self.lookup((), app, name)
        if app is None: 
            raise AppLookupError(app, name)
        if isinstance(app, App):
            app = self._app(name, app.path)
        return app

    def set(self, app, appspace, name, info=''):
        '''app registrar'''
        if isinstance(app, (str, tuple)):
            app = App(app)
        self.register((), appspace, name, app)
        
    def set_live(self, app, name, info=''):
        '''live app registrar'''
        self.register((), AApp, name, app)
        

global_appspace = AppspaceManager()