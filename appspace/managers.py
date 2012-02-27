# -*- coding: utf-8 -*-
'''appspace management'''

import re
import unicodedata
from functools import partial

from stuf.six import strings, u

from appspace.utils import lazy_import, checkname
from appspace.registry import Registry, StrictRegistry
from appspace.keys import (
    ALazyLoad, AManager, ANamespace, AppLookupError, appifies)

__all__ = ('LazyLoad', 'Manager', 'StrictManager')


class ManagerMixin(object):

    '''state manager'''

    _first = re.compile('[^\w\s-]').sub
    _second = re.compile('[-\s]+').sub

    def __init__(self, label):
        super(ManagerMixin, self).__init__()
        self._root = self._current = label
        self.ez_register(ANamespace, label, self._key)

    def apply(self, label, key=False, *args, **kw):
        '''
        call appspaced callable

        @param label: appspaced callable label
        @param key: key label (default: False)
        '''
        return self.get(label, key)(*args, **kw)

    def get(self, label, key=False):
        '''
        get thing from appspace

        @param label: appspaced thing label
        @param branch: branch label (default: False)
        '''
        key = self.namespace(key) if key else self._key
        app = self.lookup1(key, key, label)
        if app is None:
            raise AppLookupError(app, label)
        return self.load(
            label, key, app.path
        ) if ALazyLoad.providedBy(app) else app

    def load(self, label, key, module):
        '''
        import thing into appspace

        @param label: appspaced thing label
        @param module: module path
        '''
        # add branch appspace from include
        app = lazy_import(module[-1]) if isinstance(
            module, tuple
        ) else lazy_import(module)
        # register get
        self.register([key], key, label, app)
        return app

    def namespace(self, label):
        '''
        fetch key

        @param key: key
        '''
        this = self.lookup1(ANamespace, ANamespace, label)
        if this is None:
            raise AppLookupError(this, label)
        return this

    def partial(self, call, key=False, *args, **kw):
        '''
        partialize callable or appspaced application with any passed parameters

        @param call: callable or appspaced object label
        @param branch: key label (default: False)
        '''
        return partial(
            self.get(call, key), *args, **kw
        ) if isinstance(call, strings) else partial(call, *args, **kw)

    safename = staticmethod(checkname)

    def set(self, label=False, thing=False, key=False):
        '''
        add thing to appspace

        @param label: new appspace thing label (default: False)
        @param key: key label (default: False)
        @param thing: new appspace thing (default: False)
        '''
        thing = LazyLoad(thing) if isinstance(
            thing, (strings, tuple)
        ) else thing
        key = self.namespace(key) if key else self._key
        self.register([key], key, label, thing)
        return thing

    @classmethod
    def slugify(cls, value):
        '''
        normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens
        '''
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        return cls._second('-', u(cls._first('', value).strip().lower()))


@appifies(AManager)
class Manager(ManagerMixin, Registry):

    '''state manager'''

    __slots__ = ('_current', '_root', '_key', '_ns', '_first', '_second')


@appifies(AManager)
class StrictManager(ManagerMixin, StrictRegistry):

    '''strict manager'''

    __slots__ = ('_current', '_root', '_key', '_ns', '_first', '_second')


@appifies(ALazyLoad)
class LazyLoad(object):

    '''lazy import loader'''

    __slots__ = ['path']

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'lazy import from {path}'.format(path=self.path)


iskeyed = Manager.iskeyed
