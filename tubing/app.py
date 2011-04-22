'''tubing application core'''

from inspect import isroutine, isclass

from tubing.util import name_resolver, checkname, reify
from tubing.exception import NoAppError, AppLookupError
from tubing.appspace import AAppSpace, AApp, AppSpace, global_appspace

def appconf(appspace, *args, **kw):
    return App(AppFactory(appspace, *args, **kw).appspace)

def include(path):
    return ('include', path)

def patterns(appspace, *args, **kw):
    return AppFactory(appspace, *args, **kw)


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
        self._appconf = kw.get('appconf', 'apps')
        self._appname = kw.get('apppath', 'apps')
        self._defapp = kw.get('appmark', AApp)
        self._defspace = kw.get('appspace', AAppSpace)
        self._global = kw.get('use_global', False)
        if isinstance(name, tuple) and name:
            self._name = self._checkname(name[0])
            nombus = name[1:]
            if nombus:
                newaf = AppFactory(nombus, *args, **kw).appspace
            else:
                newaf = AppFactory(self._name, *args, **kw).appspace
            self._s(newaf, self._defspace, self._name)
        elif isinstance(name, basestring):
            self._name = name
            self._s(self._appspace, self._defspace, name)
            apper = self._a
            mod = self._i
            for name, path in args:
                if isinstance(path, basestring):
                    apper(name, path)
                elif isinstance(path, tuple):
                    mod(name, path)

    @reify
    def _checkname(self):
        return checkname

    @reify
    def _nresolve(self):
        return name_resolver.resolve

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

    def _a(self, name, path):
        self._g(self._defspace, self._name).setapp(self._l(path), AApp, name)

    def _l(self, dotted):
        return self._nresolve(dotted)

    def _i(self, name, path):
        self._s(
            getattr(
                self._l('.'.join([path[-1], self._appname])), self._appconf,
            ).appspace,
            self._defspace,
            name,
        )

    def _s(self, app, appspace, name='', event=False):
        return self._sa(app, appspace, name, app.__doc__, event)


class App(AppBase):

    def __init__(self, appspace):
        self._appspace = appspace

    def __call__(self, name, *args, **kw):
        if not isinstance(name, tuple):
            return self._sort(self._resolve(name), *args, **kw)
        obj = self
        for n in name:
            obj = obj._resolve(n)
            if not isinstance(obj, App): return self._sort(obj, *args, **kw)

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

    def _getspace(self, name=None):
        return self._q(AAppSpace, name, self._appspace)

    def _resolve(self, name):
        try:
            return self._g(AApp, name)
        except AppLookupError:
            try:
                return App(self._getspace(name))
            except AppLookupError:
                raise NoAppError('%s' % name)

    def _sort(self, result, *args, **kw):
        if isroutine(result): return result.__call__(*args, **kw)
        if isclass(result): return result.__init__(*args, **kw)
        return result


# Global app shortcut
app = App(global_appspace)