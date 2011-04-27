'''appspace state management'''

from zope.interface import implements as appifies
from zope.interface.adapter import AdapterRegistry
from zope.interface.interface import InterfaceClass as AppSpacer

from appspace.error import AppLookupError

# appspace key
AppspaceKey = AppSpacer('AppspaceKey')


class AApp(AppspaceKey):

    '''App key'''


class AAppspaceManager(AppspaceKey):

    '''AppspaceManager key'''

    def get(): #@NoSelf
        '''Get an app'''

    def set(): #@NoSelf
        '''App registration'''


class AAppspace(AppspaceKey):

    def __init__(self, appspace):
        '''@param appspace: configured appspace'''

    def __call__(self, name, *args, **kw):
        '''@param name: name of app in appspace'''

    def __contains__(name=''): #@NoSelf
        pass

    def __getitem__(name=''): #@NoSelf
        pass

    def __getattr__(name=''): #@NoSelf
        pass


class AppspaceManager(object):

    '''Default appspace state manager'''

    appifies(AAppspaceManager)

    def __init__(self, name=''):
        self._name = name
        self._appspace = AdapterRegistry()
        self._apps = dict()

    def get(self, app, name=''):
        '''App fetcher'''
        app = self._appspace.lookup((), app, name)
        if app is None: raise AppLookupError(app, name)
        return app

    def set(self, app, appspace, name, info=''):
        '''App registrar'''
        reg = self._apps.get((appspace, name))
        # already registered
        if reg is not None and reg == (app, info): return None
        subscribed = False
        for ((p, _), data) in self._apps.iteritems():
            if p == appspace and data[0] == app:
                subscribed = True
                break
        self._apps[(appspace, name)] = app, info
        self._appspace.register((), appspace, name, app)
        if not subscribed: self._appspace.subscribe((), appspace, app)


# global appspace
global_appspace = AppspaceManager('global')