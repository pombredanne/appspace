# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,f0401,e0213,e0211
'''keys'''

from __future__ import absolute_import

from zope.interface.interface import InterfaceClass as Appspacer, Attribute

AppspaceKey = Appspacer('AppspaceKey')


class AApp(AppspaceKey):

    '''app key'''


class AAppspaceManager(AppspaceKey):

    '''appspace manager key'''

    settings = Attribute('settings for an appspace')
    queue = Attribute('queue for an appspace')

    def get(label):  # @NoSelf
        '''Get an component'''

    def set(label, component):  # @NoSelf
        '''App registration'''


class AAppspace(AppspaceKey):

    '''appspace key'''

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


class ABranch(AppspaceKey):

    '''branch key'''

    def build():  # @NoSelf
        pass


class ALazyApp(AApp):

    '''lazy app key'''

    path = Attribute('module import path')


class ANamespace(AppspaceKey):

    '''namespace key'''


class AQueue(AppspaceKey):

    '''queue key'''

    def add_left(value):  # @NoSelf
        '''add item to left side of queue'''

    def pop_left():  # @NoSelf
        '''pop leftmost item in queue'''

    def add_right(value):  # @NoSelf
        '''add item to left side of queue'''

    def pop_right():  # @NoSelf
        '''pop leftmost item in queue'''


class ASettings(AppspaceKey):

    '''settings'''


class ADefaultSettings(ASettings):

    '''default settings key'''


class ARequiredSettings(ASettings):

    '''internal settings'''
