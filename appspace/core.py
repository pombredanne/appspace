# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
'''keys'''

from __future__ import absolute_import

from zope.interface.interfaces import ComponentLookupError
from zope.interface.adapter import AdapterRegistry as AppStore
from zope.interface.interface import InterfaceClass as Appspacer, Attribute
from zope.interface import (
    implements as appifies, directlyProvides as apped, providedBy as get_apps)

# primary key
AppspaceKey = Appspacer('AppspaceKey')
# app lookup exception
AppLookupError = ComponentLookupError


class AApp(AppspaceKey):

    '''app key'''
    
    
class AAppQuery(list):

    def __call__(label, *args, **kw):
        '''@param label: label of app in appspace'''

    def app(label, component, branch='', use_global=False):
        '''
        add new component to appspace

        @param label: label for branch appspace
        @param component: new component
        @param branch: branch to add component to
        @param use_global: use global appspace (default: False)
        '''

    def branch(label, use_global=False):
        '''
        add new appspace to existing appspace

        @param label: label of new appspace
        @param use_global: use global appspace (default: False)
        '''

    def get(label, branch=''):
        '''
        get component from appspace

        @param label: label for branch appspace
        @param branch: branch to add component to
        '''

    def patterns(label, *args, **kw):
        '''
        configuration for branch appspace

        @param label: name of branch appspace
        @param *args: tuple of module paths or component inclusions
        '''

    def register(klass):
        '''
        add appspace to class

        @param appspace: appspace to add
        '''


class AAppspace(AppspaceKey):

    '''appspace key'''

    appspace = Attribute('appspace manager')

    def __call__(label, *args, **kw):
        '''@param label: label of app in appspace'''

    def __contains__(label):
        '''membership check'''

    def __getattr__(label):
        pass

    def __getitem__(label):
        pass


class AAppspaceManager(AppspaceKey):

    '''manager key'''

    events = Attribute('event handler')
    settings = Attribute('settings for an appspace')

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
        pass


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

    '''settings key'''


class ADefaultSettings(ASettings):

    '''default settings key'''


class ARequiredSettings(ASettings):

    '''required settings key'''


class ATraitType(AppspaceKey):

    '''trait property key'''
