'''tubing application namespace management'''

from zope.component.registry import Components
from zope.interface import implements as appifies
from zope.interface.interface import InterfaceClass as AppSpacer

from appspace.util import reify

# appspace key
AppSpaceKey = AppSpacer('AppSpaceKey')


class AApp(AppSpaceKey):

    '''Usual app key'''


class AAppSpace(AppSpaceKey):

    '''Appspace key'''

    def getapp(): #@NoSelf
        '''Get an app'''

    def askapp(): #@NoSelf
        '''Ask for an app'''

    def setapp(): #@NoSelf
        '''App registr'''

    def deleteapp(): #@NoSelf
        ''''Delete app'''


class AppSpace(Components):

    '''Default appspace state manager'''

    appifies(AAppSpace)

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

    @reify
    def deleteapp(self):
        '''App deleter'''
        return self.unregisterUtility


class ADefaultAppKey(AppSpaceKey):

    '''Default app key key'''

# global appspace
global_appspace = AppSpace('global')