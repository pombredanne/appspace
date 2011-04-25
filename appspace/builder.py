'''appspace builder'''

from appspace.error import AppLookupError
from appspace.util import lazy, lru_cache
from appspace.state import AAppspace, AApp, Appspace, global_appspace

def appconf(appspace, *args, **kw):
    '''Configuration for root appspace

    @param appspace: name of root appspace
    '''
    return App(AppspaceFactory(appspace, *args, **kw).appspace)

def include(path):
    '''Load a branch appspace

    @param path: dotted python module import path
    '''
    return ('include', path)

def patterns(appspace, *args, **kw):
    '''Configuration for branch appspace

    @param appspace: name of branch appspace
    '''
    return AppspaceFactory(appspace, *args, **kw)


class AppspaceBase(object):

    '''Shared appspace base'''

    @lazy
    def _g(self):
        '''State app fetcher'''
        return self._appspace.getapp

    @lazy
    def _q(self):
        '''State app querier'''
        return self._appspace.askapp


class AppspaceFactory(AppspaceBase):

    '''Appspace factory'''

    def __init__(self, name, *args, **kw):
        '''@param name: name of appspace'''
        # name of branch appspace module e.g. someapp.apps
        self._appconf = kw.get('appconf', 'apps')
        # name of appspace in branch appspace module e.g. someapp.apps.apps
        self._appname = kw.get('appname', 'apps')
        # use global appspace instead of local appspace
        self._global = kw.get('use_global', False)
        # handle tuple hierarchy
        if isinstance(name, tuple) and name:
            self._name = name[0]
            nombus = name[1:]
            if nombus:
                # create tree of branch appspaces
                newaf = AppspaceFactory(nombus, *args, **kw).appspace
            else:
                # create branch appspace
                newaf = AppspaceFactory(self._name, *args, **kw).appspace
            self._s(newaf, AAppspace, self._name)
        elif isinstance(name, basestring):
            self._name = name
            # register branch appspace
            self._s(self._appspace, AAppspace, name)
            apper = self._app
            # register apps in appspace
            for arg in args: apper(*arg)

    @staticmethod
    def _dotted(value):
        '''Python dynamic loader'''
        if isinstance(value, basestring):
            name = value.split('.')
            used = name.pop(0)
            found = __import__(used)
            for n in name:
                used += '.' + n
                try:
                    found = getattr(found, n)
                except AttributeError:
                    __import__(used)
                    found = getattr(found, n) # pragma: no cover
            return found
        return value

    @lazy
    def _s(self):
        '''Appspace registration'''
        return self._appspace.setapp

    @lazy
    def appspace(self):
        '''Appspace state'''
        # using global appspace
        if self._global: return global_appspace
        # using local appspace
        return Appspace(self._name)

    @lazy
    def _appspace(self):
        # compatibility with AppspaceBase
        return self.appspace

    def _app(self, name, path):
        '''Register appspaces or apps in appspace
        @param name: name of app or appspace
        @param path: name of app or appspace on Python path
        '''
        # register app
        if isinstance(path, basestring):
            self._g(AAppspace, self._name).setapp(
                self._dotted(path), AApp, name,
            )
        # register branch appspace from included module
        elif isinstance(path, tuple):
            self._s(
                getattr(
                    self._dotted('.'.join([path[-1], self._appname])),
                    self._appconf,
                ).appspace,
                AAppspace,
                name,
                app.__doc__,
            )
        else:
            self._g(AAppspace, self._name).setapp(
                self._dotted(path), AApp, name,
            )


class App(AppspaceBase):

    def __init__(self, appspace):
        '''@param appspace: configured appspace'''
        self._appspace = appspace

    @lru_cache()
    def __call__(self, name, *args, **kw):
        '''@param name: name of app in appspace'''
        # handle non hierarchial appspace
        if not isinstance(name, tuple):
            return self._sort(self._resolve(name), *args, **kw)
        # handle hierarchial namespace in tuple
        obj = self
        for n in name:
            obj = obj._resolve(n)
            # recur through appspaces until app is found
            if not isinstance(obj, App): return self._sort(obj, *args, **kw)

    def __contains__(self, name):
        try:
            self._g(AApp, name)
            return True
        except AppLookupError:
            return False

    def __getitem__(self, name):
        return self._resolve(name)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self._resolve(name)

    @lru_cache()
    def _getspace(self, name=None):
        '''Fetch appropriate appspace

        @param name: name of appspace
        '''
        return self._q(AAppspace, name, self._appspace)

    @lru_cache()
    def _resolve(self, name):
        '''Resolve name of app in in appspace

        @param name: app name
        '''
        try:
            return self._g(AApp, name)
        except AppLookupError:
            # return appspace if no app is found to traverse appspace
            return App(self._getspace(name))

    @staticmethod
    def _sort(result, *args, **kw):
        '''Sorts between funcs/classes on one hand and non func/classes on other

        @param result: object to be sorted
        '''
        try:
            return result(*args, **kw)
        except TypeError:
            return result


# Global appspace shortcut
app = App(global_appspace)