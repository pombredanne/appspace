# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''appspace keys'''

from __future__ import unicode_literals

from inspect import ismodule

from six import iteritems
from zope.interface.adapter import AdapterRegistry
from zope.interface.interfaces import ComponentLookupError
from zope.interface.interface import InterfaceClass, Attribute
from zope.interface import implementer, directlyProvides, providedBy

AppStore = AdapterRegistry
apped = directlyProvides
appifies = implementer
get_apps = providedBy
# primary key
AppspaceKey = InterfaceClass('AppspaceKey')
# app lookup exception
AppLookupError = ComponentLookupError


class AApp(AppspaceKey):

    '''app key'''


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

    def build():
        '''build appspace'''


class ALazyApp(AApp):

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


class ANamespace(AppspaceKey):

    '''namespace key'''
    
    
class ConfigurationError(Exception):

    '''appspace configuration exception'''


class NoAppspaceError(Exception):

    '''no appspace found error'''


class NoAppError(Exception):

    '''mo application found exception'''
    
    
__all__ = sorted(name for name, obj in iteritems(locals()) if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
