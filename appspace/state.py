'''appspace state management'''

from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry
from zope.interface.interface import InterfaceClass as Appspacer

from appspace.util import lru_cache
from appspace.error import AppLookupError

AppspaceKey = Appspacer('AppspaceKey')


class AApp(AppspaceKey):

    '''App key'''


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


class AppspaceManager(AdapterRegistry):

    '''Appspace state manager'''

    __slots__ = ['_apps']

    appifies(AAppspaceManager)

    def __init__(self):
        super(AppspaceManager, self).__init__(())
        self._apps = dict()

    @lru_cache()
    def get(self, app, name=''):
        '''App fetcher'''
        app = self.lookup((), app, name)
        if app is None: raise AppLookupError(app, name)
        return app

    def set(self, app, appspace, name, info=''):
        '''App registrar'''
        reg = self._apps.get((appspace, name))
        # already registered
        if reg is not None and reg == (app, info): return None
        self._apps[(appspace, name)] = app, info
        self.register((), appspace, name, app)


global_appspace = AppspaceManager()