# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
'''appspace keys'''

from inspect import ismodule

from stuf.six import items
# pylint: disable-msg=f0401
from stuf.six.moves import filter, map
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
ifilter = filter
imap = map
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

    def __contains__(label):
        '''membership check'''

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

    events = Attribute('event handler')
    settings = Attribute('settings for an appspace')

    def __contains__(label):
        '''membership check'''

    def get(label):
        '''
        fetch instance

        @param label: instance or branch label
        '''

    def load(label, module_path):
        '''
        load branch or instance from appspace

        @param label: instance or branch label
        @param module_path: Python module path
        '''

    def set(label, instance):
        '''
        register branches or components in appspace

        @param label: appspace label
        @param instance: instance to add to appspace
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
    
    
__all__ = sorted(name for name, obj in items(locals()) if not any([
    name.startswith('_'), ismodule(obj),
]))
del ismodule
