# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,e1002,f0401,e1101,e1001
'''appspace state management'''

from __future__ import absolute_import, unicode_literals, print_function

from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry

from .error import AppLookupError 
from .util import deferred_import
from .keys import AAppspaceManager, AApp, ALazyApp


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
    
    __slots__ = ['_label']

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
            component = deferred_import(module_path[-1], self._label)
        # register component
        else:
            component = deferred_import(module_path)
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
        
        
# global appspace
global_appspace = AppspaceManager()