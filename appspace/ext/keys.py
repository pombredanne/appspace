# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=e0213,e0211
'''extension keys'''

from __future__ import absolute_import

from appspace.keys import AppspaceKey, Attribute


class AEvent(AppspaceKey):

    '''event key'''

    priority = Attribute('priority of event')


class AEventManager(AppspaceKey):

    def bind(label, instance):
        '''
        bind instance to event

        @param label: event label
        @param instance: object to bind to event
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
    
    
class ASettings(AppspaceKey):

    '''settings key'''


class ADefaultSettings(ASettings):

    '''default settings key'''


class ARequiredSettings(ASettings):

    '''required settings key'''


__all__ = (
    'ADefaultSettings', 'AEvent', 'AEventManager', 'ARequiredSettings',
    'ASettings',
)
