'''tubing application core'''

import inspect

from tubing.util import name_resolver, checkname, reify
from tubing.exception import NoAppError, ComponentLookupError
from tubing.appspace import (
    ARootAppSpace, AAppSpace, ARootApp, AApp, AppSpace, global_appspace, AEvent,
    ARootEvent)


class AppBase(object):

    @reify
    def _ga(self):
        return self._appspace.getapp

    @reify
    def _qa(self):
        return self._appspace.askapp

    def _g(self, app, name=u''):
        return self._ga(app, name)

    def _q(self, app, name=u'', default=None):
        return self._qa(app, name, default)


class AppFactory(AppBase):

    def __init__(self, name, *args, **kw):
        self._applist = kw.get('applist', 'apps')
        self._appname = kw.get('appname', 'apps')
        self._defapp = kw.get('defapp', AApp)
        self._defkw = kw.get('defkw', {})
        self._defspace = kw.get('defspace', AAppSpace)
        self._global = kw.get('global', False)
        if isinstance(name, tuple) and name:
            self._name = self._checkname(name[0])
            nombus = name[1:]
            if nombus:
                newreg = AppFactory(nombus, *args, **kw).appspace
            else:
                newreg = AppFactory(self._name, *args, **kw).appspace
            self._s(newreg, self._defspace, self._name)
        elif isinstance(name, basestring):
            self._name = name
            self._s(self._appspace, self._defspace, name)
            apper = self._app
            for arg in args: apper(*arg)

    @reify
    def _checkname(self):
        return checkname

    @reify
    def _nresolve(self):
        return name_resolver.maybe_resolve

    @reify
    def _sa(self):
        return self._appspace.setapp

    @reify
    def appspace(self):
        if self._global: return global_appspace
        return AppSpace(self._name)

    @reify
    def _appspace(self):
        return self.appspace

    def _app(self, name, path, kw=None):
        s = self._s
        mdotted = self._dotted
        if kw is None: kw = self._defkw
        if isinstance(name, (list, tuple)):
            space, path = name
            module = mdotted(path)
            include = getattr(getattr(module, self._appname), self._applist)
            registry = include.appspace()
            if registry != global_appspace: s(registry, self._defspace, space)
        elif isinstance(name, basestring):
            app = mdotted(path)
            aspace = self._q(self._defspace, kw.get('appspace', self._name))
            event = kw.get('event', False)
            if event:
                akey = AEvent
                adef = ARootEvent
            else:
                akey = AApp
                adef = ARootApp
            aspace.setapp(app, akey, name)
            if kw.get('default', False): aspace.setaap(adef, app)

    def _dotted(self, dotted):
        return self._nresolve(dotted)

    def _s(self, app, appspace, name='', event=False):
        return self._sa(app, appspace, name, event=event)


class App(AppBase):

    def __init__(self, registry):
        self._appspace = registry

    def __call__(self, name, *args, **kw):
        if not isinstance(name, tuple):
            obj = self._resolve(name)
        else:
            obj = self
            for n in name:
                obj = obj._resolve(n)
                if isinstance(obj, App): break
        return self._sortout(obj, *args, **kw)

    def __contains__(self, name):
        try:
            self._resolve(name)
            return True
        except NoAppError:
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
    def _rootapp(self):
        return self._q(ARootApp)

    def _getspace(self, name=None):
        if name is not None: return self._g(AAppSpace, name)
        return self._appspace

    def _resolve(self, name):
        try:
            default = self._rootapp
            if default: return self._q(AApp, name, default)
            return self._g(AApp, name)
        except ComponentLookupError:
            try:
                return App(self._getspace(name))
            except ComponentLookupError:
                raise NoAppError('%s' % name)

    def _sortout(self, result, *args, **kw):
        inspecting = inspect
        if inspecting.isfunction(result):
            return result.__call__(*args, **kw)
        if inspecting.isclass(result):
            return result.__init__(*args, **kw)
        if inspecting.ismethod(result):
            return result.__call__(*args, **kw)
        if inspecting.isbuiltin(result):
            return result.__call__(*args, **kw)
        return result


# Global app shortcut
app = App(global_appspace)

def appconfig(appspace, *args, **kw):
    return App(AppFactory(appspace, *args, **kw).appspace)

def include(appspace, path):
    return appspace, path

def patterns(appspace, *args, **kw):
    return AppFactory(appspace, *args, **kw)