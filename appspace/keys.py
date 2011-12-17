# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,f0401,e0213,e0211
'''appspace keys'''

from __future__ import absolute_import

from zope.interface.interface import InterfaceClass as Appspacer, Attribute

AppspaceKey = Appspacer('AppspaceKey')


class AApp(AppspaceKey):

    '''App key'''


class ALazyApp(AApp):

    '''App lazy key'''

    path = Attribute('module import path')


class AAppspaceManager(AppspaceKey):

    '''AppspaceManager key'''

    settings = Attribute('settings for an appspace')
    queue = Attribute('queue for an appspace')
    cache = Attribute('cache for an appspace')

    def get(label):  # @NoSelf
        '''Get an component'''

    def set(label, component):  # @NoSelf
        '''App registration'''


class AAppspace(AppspaceKey):

    '''Appspace key'''

    appspace = Attribute('appspace manager')

    def __init__(appspace):  # @NoSelf
        '''@param appspace: configured appspace'''

    def __call__(label, *args, **kw):  # @NoSelf
        '''@param label: label of app in appspace'''

    def __contains__(label):  # @NoSelf
        '''membership check'''

    def __getattribute__(label):  # @NoSelf
        pass

    def __getitem__(label):  # @NoSelf
        pass


class ASettings(AppspaceKey):

    '''settings'''


class AInternalSettings(ASettings):

    '''internal settings'''


class ADefaultSettings(ASettings):

    '''default settings key'''


class AQueue(AppspaceKey):

    '''queue'''

    def add_left(value):  # @NoSelf
        '''add item to left side of queue'''

    def pop_left():  # @NoSelf
        '''pop leftmost item in queue'''

    def add_right(value):  # @NoSelf
        '''add item to left side of queue'''

    def pop_right():  # @NoSelf
        '''pop leftmost item in queue'''
