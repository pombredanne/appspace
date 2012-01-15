# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''extension keys'''

from __future__ import absolute_import

from inspect import ismodule

from appspace.keys import AppspaceKey, Attribute


class AClient(AppspaceKey):

    '''appspace client key'''


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


class AMaster(AppspaceKey):

    '''appspace master key'''


class AServer(AppspaceKey):

    '''appspace server key'''


class AService(AppspaceKey):

    '''appspace service'''


class AServiceManager(AppspaceKey):

    '''appspace service manager'''
    
    
class ASettings(AppspaceKey):

    '''settings key'''


class ADefaultSettings(ASettings):

    '''default settings key'''


class ARequiredSettings(ASettings):

    '''required settings key'''


class ASynched(AppspaceKey):
    
    '''synced key'''


class NoDefault(object):

    '''no default'''

    def generate(self, klass):
        '''generator'''


class Undefined(object):

    '''undefined value'''


NoDefault = NoDefault()
Undefined = Undefined()

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
