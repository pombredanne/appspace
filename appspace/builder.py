'''appspace builder'''

from appspace.util import lazy, lru_cache
from appspace.error import AppLookupError, NoAppError
from appspace.state import (
    AAppspace, AApp, AppspaceManager, global_appspace, appifies,
)

def include(path):
    '''Load a branch appspace

    @param path: module import path
    '''
    return ('include', path)

def patterns(appspace, *args, **kw):
    '''Configuration for branch appspace

    @param appspace: name of branch appspace
    '''
    return AppspaceFactory(appspace, *args, **kw)()


class AppspaceFactory(object):

    '''Appspace factory'''

    def __init__(self, name, *args, **kw):
        '''@param name: name of appspace'''
        # name of branch appspace module e.g. someapp.apps
        self._appconf = kw.get('appconf', 'apps')
        # name of appspace in branch appspace module e.g. someapp.apps.apps
        self._appname = kw.get('appname', 'apps')
        # use global appspace instead of local appspace
        self._global = kw.get('use_global', False)
        # namespace
        self._name = name
        # module prefix
        self._prefix = kw.get('prefix')
        # register apps in appspace
        apper = self._app
        for arg in args: apper(*arg)
        if name: self._appspace.set(Appspace(self._appspace), AApp, self._name)

    def __call__(self):
        return Appspace(self._appspace)

    def _app(self, name, path):
        '''Register appspaces or apps in appspace

        @param name: app or appspace
        @param path: Python path
        '''
        # register branch appspace from included module
        if isinstance(path, tuple):
            self._appspace.set(
                getattr(
                    self._load('.'.join([path[-1], self._appname])),
                    self._appconf,
                ),
                AApp,
                name,
                app.__doc__,
            )
        # register app
        else:
            self._appspace.set(self._load(path), AApp, name)

    @lazy
    def _appspace(self):
        '''Appspace state'''
        # using global appspace
        if self._global: return global_appspace
        # using local appspace
        return AppspaceManager()

    def _load(self, path):
        '''Python dynamic loader

        @param path: something to load
        '''
        try:
            if self._prefix is not None: path = '.'.join([self._prefix, path])
            name = path.split('.')
            used = name.pop(0)
            found = __import__(used)
            for n in name:
                used += '.' + n
                try:
                    found = getattr(found, n)
                except AttributeError:
                    __import__(used)
                    found = getattr(found, n)
            return found
        except AttributeError:
            return path


class Appspace(object):

    __slots__ = ['_appspace']

    appifies(AAppspace)

    def __init__(self, appspace):
        '''@param appspace: configured appspace'''
        self._appspace = appspace

    def __call__(self, name, *args, **kw):
        '''@param name: name of app in appspace'''
        result = self.__getitem__(name)
        try:
            return result(*args, **kw)
        except TypeError:
            return result

    def __contains__(self, name):
        try:
            self._appspace.get(AApp, name)
            return True
        except AppLookupError:
            return False

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.__getitem__(name)

    @lru_cache()
    def __getitem__(self, name):
        try:
            return self._appspace.get(AApp, name)
        except AppLookupError:
            raise NoAppError('%s' % name)


# Global appspace shortcut
app = Appspace(global_appspace)