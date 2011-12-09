# -*- coding: utf-8 -*-
'''appspace builder'''

from __future__ import absolute_import

from .keys import AAppspace
from .util import lru_cache, lazy
from .error import AppLookupError, NoAppError
from .state import AppspaceManager, appifies, global_appspace

def add_app(appspace, label, component, branch='', use_global=False):
    '''
    add new component to appspace
    
    @param appspace: existing appspace
    @param label: label of branch appspace
    @param component: new component
    @param branch: branch to add component to
    @param use_global: use global appspace (default: False)
    '''
    if use_global:
        appspace = app
    elif branch:
        appspace = add_branch(appspace, branch)
    appspace.appspace.set(label, component)

def add_branch(appspace, label, use_global=False):
    '''
    add new appspace to existing appspace

    @param appspace: existing appspace
    @param label: label of new appspace
    @param use_global: use global appspace (default: False)
    '''
    if label not in appspace and not use_global:
        new_appspace = Appspace(AppspaceManager())
        appspace.appspace.set(label, new_appspace)
        return new_appspace
    return appspace

def include(module_path):
    '''
    load a branch appspace

    @param module_path: module import path
    '''
    return ('include', module_path)

def patterns(label, *args, **kw):
    '''
    configuration for branch appspace

    @param label: name of branch appspace
    @param *args: tuple of module paths or component inclusions 
    '''
    return AppspaceFactory(label, *args, **kw)()


class AppspaceFactory(object):

    '''Appspace factory'''

    def __init__(self, label, *args, **kw):
        '''
        @param label: label of appspace
        @param *args: tuple of module paths or component inclusions
        '''
        # label of appspace in branch appspace module e.g. someapp.apps.label
        self._label = kw.get('label', 'apps')
        # whether to use global appspace instead of local appspace
        self._global = kw.get('use_global', False)
        # appspace label
        self._label = label
        # register apps in appspace
        apper = self._appspace.set
        for arg in args:
            print arg
            apper(*arg)
        if label:
            apper(label, Appspace(self._appspace))

    def __call__(self):
        '''instantiate appspace interface'''
        return Appspace(self._appspace)
    
    @lazy
    def _appspace(self):
        '''provide appspace'''
        # using global appspace
        if self._global: 
            return global_appspace
        # using local appspace
        return AppspaceManager(self._label)


class Appspace(object):
    
    '''appspace interface'''

    __slots__ = ['appspace']

    appifies(AAppspace)

    def __init__(self, appspace):
        '''
        initialize appspace
        
        @param appspace: configured appspace
        '''
        self.appspace = appspace

    def __call__(self, label, *args, **kw):
        '''
        pass arguments to component in appspace
        
        @param label: label of component in appspace
        '''
        result = self.__getitem__(label)
        try:
            return result(*args, **kw)
        except TypeError:
            return result
        
    def __contains__(self, label):
        return label in self.appspace

    def __getattribute__(self, label):
        '''
        access component in appspace 
        
        @param label: label of component in appspace
        '''
        try:
            return object.__getattribute__(self, label)
        except AttributeError:
            return self.__getitem__(label)

    @lru_cache()
    def __getitem__(self, label):
        '''
        access component in appspace
        
        @param label: label of component in appspace
        '''
        try:
            return self.appspace.get(label)
        except AppLookupError:
            raise NoAppError('%s' % label)

    def __repr__(self):
        return self.appspace.__repr__()


# Global appspace shortcut
app = Appspace(global_appspace)