# -*- coding: utf-8 -*-
## pylint: disable-msg=w0232,f0401,e0213
from zope.interface.interface import InterfaceClass as Appspacer, Attribute

AppspaceKey = Appspacer('AppspaceKey')


class AApp(AppspaceKey):

    '''App key'''
    
    path = Attribute('module import path')
    
class AAppspaceManager(AppspaceKey):

    '''AppspaceManager key'''

    def get(app, name=''): #@NoSelf
        '''Get an app'''

    def set(app, appspace, name, info=''): #@NoSelf
        '''App registration'''


class AAppspace(AppspaceKey):

    '''Appspace key'''

    def __init__(appspace): #@NoSelf
        '''@param appspace: configured appspace'''

    def __call__(name, *args, **kw): #@NoSelf
        '''@param name: name of app in appspace'''

    def __contains__(name): #@NoSelf
        pass

    def __getitem__(name): #@NoSelf
        pass

    def __getattr__(name): #@NoSelf
        pass
