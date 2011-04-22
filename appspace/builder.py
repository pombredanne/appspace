'''appspace builder'''

from appspace.error import NoAppError, AppLookupError
from appspace.util import name_resolver, checkname, reify, lru_cache
from appspace.state import (
    AAppSpace, AApp, AppSpace, global_appspace, ADefaultAppKey)

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

    @reify
    def _g(self):
        '''State app fetcher'''
        return self._appspace.getapp

    @reify
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
        # default appspace key
        self._defapp = kw.get('app', AApp)
        # use global appspace instead of local appspace
        self._global = kw.get('use_global', False)
        # handle tuple hierarchy
        if isinstance(name, tuple) and name:
            self._name = self._checkname(name[0])
            nombus = name[1:]
            if nombus:
                # create tree of branch appspaces
                newaf = AppspaceFactory(nombus, *args, **kw).appspace
            else:
                # create branch appspace
                newaf = AppspaceFactory(self._name, *args, **kw).appspace
            self._s(newaf, AAppSpace, self._name)
        elif isinstance(name, basestring):
            self._name = name
            # register default app key for appspace
            self._s(self._defapp, ADefaultAppKey)
            # register branch appspace
            self._s(self._appspace, AAppSpace, name)
            apper = self._app
            # register apps in appspace
            for arg in args: apper(*arg)

    @reify
    def _checkname(self):
        '''Make sure name is Python safe'''
        return checkname

    @reify
    def _dotted(self):
        '''Python dynamic loader'''
        return name_resolver.resolve

    @reify
    def _s(self):
        '''Appspace registration'''
        return self._appspace.setapp

    @reify
    def appspace(self):
        '''Appspace state'''
        # using global appspace
        if self._global: return global_appspace
        # using local appspace
        return AppSpace(self._name)

    @reify
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
            self._g(AAppSpace, self._name).setapp(
                self._dotted(path), self._defapp, name,
            )
        # register branch appspace from included module
        elif isinstance(path, tuple):
            self._s(
                getattr(
                    self._dotted('.'.join([path[-1], self._appname])),
                    self._appconf,
                ).appspace,
                AAppSpace,
                name,
                app.__doc__,
            )


class App(AppspaceBase):

    def __init__(self, appspace):
        '''@param appspace: configured appspace'''
        self._appspace = appspace

    @lru_cache(100)
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
        else:
            return None

    def __contains__(self, name):
        try:
            self._g(self._defapp, name)
            return True
        except AppLookupError:
            return False

    def __getitem__(self, name):
        try:
            return self._resolve(name)
        except NoAppError:
            raise NoAppError('%s' % name)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self._resolve(name)

    @reify
    def _defapp(self):
        '''Default app key'''
        return self._g(ADefaultAppKey)

    @lru_cache()
    def _getspace(self, name=None):
        '''Fetch appropriate appspace

        @param name: name of appspace
        '''
        return self._q(AAppSpace, name, self._appspace)

    @lru_cache()
    def _resolve(self, name):
        '''Resolve name of app in in appspace
        @param name: app name
        '''
        try:
            return self._g(self._defapp, name)
        except AppLookupError:
            # return appspace if no app is found to traverse appspace
            return App(self._getspace(name))

    def _sort(self, result, *args, **kw):
        '''Sorts between funcs/classes on one hand and non func/classes on other

        @param result: object to be sorted
        '''
        try:
            return result(*args, **kw)
        except TypeError:
            return result


# Global appspace shortcut
app = App(global_appspace)