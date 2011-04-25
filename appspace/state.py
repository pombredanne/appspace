'''appspace state management'''

from zope.component.registry import Components
from zope.interface import implements as appifies
from zope.interface.interface import InterfaceClass as AppSpacer

from appspace.util import lazy

# appspace key
AppspaceKey = AppSpacer('AppspaceKey')


class AApp(AppspaceKey):

    '''App key'''


class AAppspaceManager(AppspaceKey):

    '''AppspaceManager key'''

    def getapp(): #@NoSelf
        '''Get an app'''

    def askapp(): #@NoSelf
        '''Ask for an app'''

    def setapp(): #@NoSelf
        '''App registration'''


class AAppspace(AppspaceKey):

    def __init__(self, appspace):
        '''@param appspace: configured appspace'''
        self._appspace = appspace

    def __call__(self, name, *args, **kw):
        '''@param name: name of app in appspace'''

    def __contains__(name): #@NoSelf
        pass

    def __getitem__(name): #@NoSelf
        pass

    def __getattr__(name): #@NoSelf
        pass

    def _getspace(name=None): #@NoSelf
        '''Fetch appropriate appspace

        @param name: name of appspace
        '''

    def _resolve(name): #@NoSelf
        '''Resolve name of app in appspace

        @param name: app name
        '''

    def _sort(result, *args, **kw): #@NoSelf
        '''Sorts between funcs/classes on one hand and non func/classes on other
        '''


class AppspaceManager(Components):

    '''Default appspace state manager'''

    appifies(AAppspaceManager)

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
global_appspace = AppspaceManager('global')