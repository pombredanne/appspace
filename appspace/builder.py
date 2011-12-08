# -*- coding: utf-8 -*-
'''appspace builder'''

from __future__ import absolute_import

from .keys import AAppspace, AApp
from .util import lazy, lru_cache
from .error import AppLookupError, NoAppError
from .state import AppspaceManager, global_appspace, appifies

def add_app(appspace, name, new_app, branch='', use_global=False):
    '''
    add new app to existing namespace
    
    @param appspace: existing appspace
    @param name: name of branch appspace
    '''
    if branch:
        appspace = add_branch(appspace, branch)
    elif use_global:
        appspace = global_appspace
    appspace.appspace.set_live(new_app, name)

def add_branch(appspace, name):
    '''
    add new appspace to existing appspace

    @param appspace: existing appspace
    @param name: name of new appspace
    '''
    new_appspace = Appspace(AppspaceManager())
    appspace.set(new_appspace, AApp, name)
    return new_appspace

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
        # name of appspace in branch appspace module e.g. someapp.apps.appconf
        self._appconf = kw.get('appconf', 'appconf')
        # whether to use global appspace instead of local appspace
        self._global = kw.get('use_global', False)
        # namespace
        self._name = name
        # register apps in appspace
        apper = self._app
        for arg in args: 
            apper(*arg)
        if name: 
            self._add_branch(name)

    def __call__(self):
        return Appspace(self._appspace)
    
    def _add_branch(self, name):
        '''
        add new branch appspace
    
        @param name: name of branch appspace
        '''
        self._appspace.set(Appspace(self._appspace), AApp, name)
    
    def _app(self, name, new_app):
        self._appspace.set(new_app, AApp, name)

    @lazy
    def _appspace(self):
        '''
        appspace state
        '''
        # using global appspace
        if self._global: 
            return global_appspace
        # using local appspace
        return AppspaceManager(self._appconf)


class Appspace(object):

    __slots__ = ['appspace']

    appifies(AAppspace)

    def __init__(self, appspace):
        '''
        @param appspace: configured appspace
        '''
        self.appspace = appspace

    def __call__(self, name, *args, **kw):
        '''@param name: name of app in appspace'''
        result = self.__getitem__(name)
        try:
            return result(*args, **kw)
        except TypeError:
            return result

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.__getitem__(name)

    @lru_cache()
    def __getitem__(self, name):
        try:
            return self.appspace.get(AApp, name)
        except AppLookupError:
            raise NoAppError('%s' % name)


# Global appspace shortcut
app = Appspace(global_appspace)