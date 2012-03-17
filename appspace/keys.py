# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
'''appspace keys'''

# pylint: disable-msg=f0401
from zope.interface.interfaces import ComponentLookupError
from zope.interface.interface import InterfaceClass, Attribute
from zope.interface import implementer, directlyProvides, providedBy
from zope.interface.adapter import AdapterRegistry, VerifyingAdapterRegistry
# pylint: enable-msg=f0401

AppStore = AdapterRegistry
StrictAppStore = VerifyingAdapterRegistry
apped = directlyProvides
appifies = implementer
get_apps = providedBy
# primary key
AppspaceKey = InterfaceClass('AppspaceKey')
# app lookup exception
AppLookupError = ComponentLookupError


class AApp(AppspaceKey):

    '''app key'''


# pylint: disable-msg=e0213
class AAppspace(AppspaceKey):

    '''appspace key'''

    manager = Attribute('appspace manager')

    def __call__(label, *args, **kw):
        '''@param label: label of app in appspace'''

    def __getattr__(label):
        '''get attribute'''

    def __getitem__(label):
        '''get item'''
        

class ABranch(AppspaceKey):

    '''branch key'''

# pylint: disable-msg=e0211
    def build():
        '''build appspace'''
# pylint: enable-msg=e0211


class ALazyLoad(AApp):

    '''lazy app key'''

    path = Attribute('import path')


class AManager(AppspaceKey):

    '''appspace key'''
    
    def apply(label, key=False, *args, **kw):
        '''
        invoke appspaced callable

        @param label: appspaced callable
        @param key: key label (default: False)
        '''

    def get(label, key=False):
        '''
        get thing from appspace

        @param label: appspaced thing label
        @param key: appspace key (default: False)
        '''

    def load(label, key, module):
        '''
        import thing into appspace

        @param label: appspaced thing label
        @param key: appspace key
        @param module: module path
        '''
        
    def namespace(label):
        '''
        fetch key

        @param label: appspace key label
        '''
        
    def partial(call, key=False, *args, **kw):
        '''
        partialize callable or appspaced application with any passed parameters

        @param call: callable or appspaced object label
        @param key: appspace key label (default: False)
        '''
        
    def set(label=False, thing=False, key=False):
        '''
        add thing to appspace

        @param label: new appspace thing label (default: False)
        @param key: key label (default: False)
        @param thing: new appspace thing (default: False)
        '''
        
    def slugify(value):
        '''
        normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens
        '''
# pylint: enable-msg=e0213


class ANamespace(AppspaceKey):

    '''namespace key'''
    
    
class ConfigurationError(Exception):

    '''appspace configuration exception'''


class NoAppspaceError(Exception):

    '''no appspace found error'''


class NoAppError(Exception):

    '''mo application found exception'''
