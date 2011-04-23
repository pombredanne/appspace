'''tubing application namespace management'''

from zope.component.registry import Components
from zope.interface import implements as appifies
from zope.interface.interface import InterfaceClass as AppSpacer

from appspace.util import reify

# appspace key
AppspaceKey = AppSpacer('AppspaceKey')


class AApp(AppspaceKey):

    '''App key'''


class AAppspace(AppspaceKey):

    '''Appspace key'''

    def getapp(): #@NoSelf
        '''Get an app'''

    def askapp(): #@NoSelf
        '''Ask for an app'''

    def setapp(): #@NoSelf
        '''App registr'''

    def deleteapp(): #@NoSelf
        ''''Delete app'''


class Appspace(Components):

    '''Default appspace state manager'''

    appifies(AAppspace)

    @reify
    def getapp(self):
        '''App fetcher'''
        return self.getUtility

    @reify
    def askapp(self):
        '''App querier'''
        return self.queryUtility

    @reify
    def setapp(self):
        '''App registrar'''
        return self.registerUtility


# global appspace
global_appspace = Appspace('global')