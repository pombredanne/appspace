# -*- coding: utf-8 -*-
'''appspace builder'''

from appspace.keys import AAppspace, AApp
from appspace.util import lazy, lru_cache
from appspace.error import AppLookupError, NoAppError
from appspace.state import AppspaceManager, global_appspace, appifies

def include(path):
    '''
    load a branch appspace

    @param path: module import path
    '''
    return ('include', path)

def patterns(appspace, *args, **kw):
    '''
    configuration for branch appspace

    @param appspace: name of branch appspace
    '''
    return AppspaceFactory(appspace, *args, **kw)()


class AppspaceFactory(object):

    '''Appspace factory'''

    def __init__(self, name, *args, **kw):
        '''
        @param name: name of appspace
        '''
        # name of branch appspace module e.g. someapp.apps
        self._appconf = kw.get('appconf', 'apps')
        # name of appspace in branch appspace module e.g. someapp.apps.apps
        self._appname = kw.get('appname', 'apps')
        # use global appspace instead of local appspace
        self._global = kw.get('use_global', False)
        # namespace
        self._name = name
        # register apps in appspace
        apper = self._app
        for arg in args: 
            apper(*arg)
        if name: 
            self._appspace.set(Appspace(self._appspace), AApp, self._name)

    def __call__(self):
        return Appspace(self._appspace)
    
    def _app(self, name, path):
        self._appspace.set(path, AApp, name)

    @lazy
    def _appspace(self):
        '''
        appspace state
        '''
        # using global appspace
        if self._global: 
            return global_appspace
        # using local appspace
        return AppspaceManager()


class Appspace(object):

    __slots__ = ['_appspace']

    appifies(AAppspace)

    def __init__(self, appspace):
        '''
        @param appspace: configured appspace
        '''
        self._appspace = appspace

    def __call__(self, name, *args, **kw):
        '''@param name: name of app in appspace'''
        result = self.__getitem__(name)
        try:
            return result(*args, **kw)
        except TypeError:
            return result

    def __contains__(self, name):
        try:
            self._appspace.get(AApp, name)
            return True
        except AppLookupError:
            return False

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.__getitem__(name)

    @lru_cache()
    def __getitem__(self, name):
        try:
            return self._appspace.get(AApp, name)
        except AppLookupError:
            raise NoAppError('%s' % name)


# Global appspace shortcut
app = Appspace(global_appspace)