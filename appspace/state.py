# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,e1002,f0401,e1101
'''appspace state management'''

from __future__ import absolute_import

from importlib import import_module

from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry

from .util import lru_cache
from .error import AppLookupError 
from .keys import AAppspaceManager, AApp, ALazyApp


class LazyApp(object):
    
    '''lazy component loader'''
    
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

    appifies(AAppspaceManager)
    
    def __init__(self, label='appconf', bases=()): 
        '''
        @param label: label for application module name
        '''
        super(AppspaceManager, self).__init__(bases)
        self._label = label
        
    def __contains__(self, label):
        return label in self.names((), AApp)
        
    def __repr__(self):
        return str(self.lookupAll((), AApp))
        
    def _component(self, label, module_path):
        '''
        register branch appspaces or apps in appspace

        @param label: component or branch appspace
        @param module_path: Python module path
        '''
        # register branch appspace from included module
        if isinstance(module_path, tuple):
            component = getattr(self._load(module_path[-1]), self._label)
        # register component
        else:
            component = self._load(module_path)
        self.set(label, component)
        return component
        
    def _load(self, module_path):
        '''
        dynamic module loader

        @param module_path: something to load
        '''
        if isinstance(module_path, str):
            try:
                dot = module_path.rindex('.')
                # import module
                module_path = getattr(
                    import_module(module_path[:dot]), module_path[dot+1:]
                )
            # If nothing but module name, import the module
            except AttributeError:
                module_path = import_module(module_path)
        return module_path

    @lru_cache()
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
        
        
# global appspace
global_appspace = AppspaceManager()