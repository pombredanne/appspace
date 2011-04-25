'''appspace state management'''

from zope.component.registry import Components
from zope.interface import implements as appifies
from zope.interface.interface import InterfaceClass as AppSpacer

from appspace.util import lazy

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
        '''App registration'''


class Appspace(Components):

    '''Default appspace state manager'''

    appifies(AAppspace)

    @lazy
    def getapp(self):
        '''App fetcher'''
        return self.getUtility

    @lazy
    def askapp(self):
        '''App querier'''
        return self.queryUtility

    @lazy
    def setapp(self):
        '''App registrar'''
        return self.registerUtility


# global appspace
global_appspace = Appspace('global')