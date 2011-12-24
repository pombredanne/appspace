# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,f0401,e0213,e0211
'''keys'''

from __future__ import absolute_import

from zope.interface.interface import InterfaceClass as Appspacer, Attribute

AppspaceKey = Appspacer('AppspaceKey')


class AApp(AppspaceKey):

    '''app key'''


class AAppspace(AppspaceKey):

    '''appspace key'''

    appspace = Attribute('appspace manager')

    def __call__(label, *args, **kw):  # @NoSelf
        '''@param label: label of app in appspace'''

    def __contains__(label):  # @NoSelf
        '''membership check'''

    def __getattr__(label):  # @NoSelf
        pass

    def __getitem__(label):  # @NoSelf
        pass


class AAppspaceManager(AppspaceKey):

    '''appspace manager key'''

    events = Attribute('event handler')
    settings = Attribute('settings for an appspace')

    def __contains__(label):  # @NoSelf
        '''membership check'''

    def get(label):  # @NoSelf
        '''
        fetch component

        @param label: component or branch label
        '''

    def load(label, module_path):  # @NoSelf
        '''
        load branch or component from appspace

        @param label: component or branch label
        @param module_path: Python module path
        '''

    def set(label, component):  # @NoSelf
        '''
        register branches or components in appspace

        @param label: appspace label
        @param component: component to add to appspace
        '''


class ABranch(AppspaceKey):

    '''branch key'''

    def build():  # @NoSelf
        pass


class AEvent(AppspaceKey):

    '''event key'''

    priority = Attribute('priority of event')


class AEventManager(AppspaceKey):

    def bind(label, component):  # @NoSelf
        '''
        bind component to event

        @param label: event label
        @param component: object to bind to event
        '''

    def burst(label, queue):  # @NoSelf
        '''
        run event subscribers on contents of queue

        @param label: event label
        @param queue: queue of arguements
        '''

    def fire(event, *args, **kw):  # @NoSelf
        '''
        fire event, passing arbitrary positional arguments and keywords

        @param appspace: existing appspace
        @param event: event label
        '''

    def get(label):  # @NoSelf
        '''
        returns event

        @param label: event label
        '''

    def react(event):  # @NoSelf
        '''
        returns objects bound to an event

        @param label: event label
        '''

    def register(label, priority=1, **kw):  # @NoSelf
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: 1)
        '''


class ALazyApp(AApp):

    '''lazy app key'''

    path = Attribute('module import path')


class ANamespace(AppspaceKey):

    '''namespace key'''


class ASettings(AppspaceKey):

    '''settings key'''


class ADefaultSettings(ASettings):

    '''default settings key'''


class ARequiredSettings(ASettings):

    '''required settings key'''
