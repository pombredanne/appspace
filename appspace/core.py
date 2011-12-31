# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''appspace core'''

from __future__ import absolute_import

from zope.interface.adapter import AdapterRegistry
from zope.interface.interfaces import ComponentLookupError
from zope.interface.interface import InterfaceClass, Attribute
from zope.interface import implements, directlyProvides, providedBy

AppStore = AdapterRegistry
appifies = implements
apped = directlyProvides
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


class AManager(AppspaceKey):

    '''appspace key'''

    events = Attribute('event handler')
    conf = Attribute('conf for an appspace')

    def __contains__(label):
        '''membership check'''

    def get(label):
        '''
        fetch component

        @param label: component or branch label
        '''

    def load(label, module_path):
        '''
        load branch or component from appspace

        @param label: component or branch label
        @param module_path: Python module path
        '''

    def set(label, component):
        '''
        register branches or components in appspace

        @param label: appspace label
        @param component: component to add to appspace
        '''


class ABranch(AppspaceKey):

    '''branch key'''

    def build():
        '''build appspace'''


class AEvent(AppspaceKey):

    '''event key'''

    priority = Attribute('priority of event')


class AEventManager(AppspaceKey):

    def bind(label, component):
        '''
        bind component to event

        @param label: event label
        @param component: object to bind to event
        '''

    def burst(label, queue):
        '''
        run event subscribers on contents of queue

        @param label: event label
        @param queue: queue of arguements
        '''

    def fire(event, *args, **kw):
        '''
        fire event, passing arbitrary positional arguments and keywords

        @param event: event label
        '''

    def get(label):
        '''
        returns event

        @param label: event label
        '''

    def react(event):
        '''
        returns objects bound to an event

        @param label: event label
        '''

    def register(label, priority=1, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: 1)
        '''


class ALazyApp(AApp):

    '''lazy app key'''

    path = Attribute('import path')


class ANamespace(AppspaceKey):

    '''namespace key'''


class ASettings(AppspaceKey):

    '''conf key'''


class ADefaultSettings(ASettings):

    '''default conf key'''


class AHost(AppspaceKey):

    '''hosted app key'''
    
    
class ADelegater(AppspaceKey):
    
    '''delegated app key'''
    

class ADelegate(AppspaceKey):
    
    '''delegatable app key'''


class ARequiredSettings(ASettings):

    '''required conf key'''


class ATraitType(AppspaceKey):

    '''trait property key'''
