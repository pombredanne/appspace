# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,f0401,e0213
from zope.interface.interface import InterfaceClass as Appspacer, Attribute

AppspaceKey = Appspacer('AppspaceKey')


class AApp(AppspaceKey):
    
    '''App key'''


class ALazyApp(AApp):

    '''App lazy key'''
    
    path = Attribute('module import path')
    
    
class AAppspaceManager(AppspaceKey):

    '''AppspaceManager key'''

    def get(label): #@NoSelf
        '''Get an component'''

    def set(label, component): #@NoSelf
        '''App registration'''


class AAppspace(AppspaceKey):

    '''Appspace key'''
    
    appspace = Attribute('appspace manager')

    def __init__(appspace): #@NoSelf
        '''@param appspace: configured appspace'''

    def __call__(label, *args, **kw): #@NoSelf
        '''@param label: label of app in appspace'''

    def __contains__(label): #@NoSelf
        '''membership check'''
    
    def __getattribute__(label): #@NoSelf
        pass

    def __getitem__(label): #@NoSelf
        pass
