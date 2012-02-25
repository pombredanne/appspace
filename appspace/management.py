# -*- coding: utf-8 -*-
'''appspace management'''

import re
import unicodedata
from functools import partial

from stuf.six import strings, u

from appspace.registry import Registry
from appspace.utils import lazy_import, checkname
from appspace.keys import ALazyLoad, AManager, AppLookupError, appifies

__all__ = ('LazyLoad', 'Manager')


@appifies(AManager)
class Manager(Registry):

    '''state manager'''

    __slots__ = ('_key', '_ns', '_first', '_second')

    _first = re.compile('[^\w\s-]').sub
    _second = re.compile('[-\s]+').sub

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
        key = self.key(key) if key else self._key
        app = self.lookup1(key, key, label)
        if app is None:
            raise AppLookupError(app, label)
        return self.load(label, app.path) if ALazyLoad.providedBy(app) else app

    def load(self, label, module):
        '''
        import thing into appspace

        @param label: appspaced thing label
        @param module: module path
        '''
        # add branch appspace from include
        app = lazy_import(
            module[-1], self._label
        ) if isinstance(module, tuple) else lazy_import(module)
        # register get
        key = self.key(module[0]) if isinstance(module, tuple) else self._key
        self.register([key], key, label, app)
        return app

    def partial(self, call, key=False, *args, **kw):
        '''
        partialize callable or appspaced application with any passed parameters

        @param call: callable or application label
        @param branch: branch label (default: False)
        '''
        return partial(
            self.get(call, key), *args, **kw
        ) if isinstance(call, strings) else partial(call, *args, **kw)

    @staticmethod
    def safename(value):
        '''ensures a string is a legal Python name'''
        return checkname(value)

    def set(self, thing, label, key=False):
        '''
        add thing to appspace

        @param thing: new appspaced thing
        @param label: appspaced thing label
        @param key: key label (default: False)
        '''
        thing = LazyLoad(thing) if isinstance(
            thing, (strings, tuple)
        ) else thing
        key = self.key(key) if key else self._key
        self.register([key], key, label, thing)
        return thing

    @classmethod
    def slugify(cls, value):
        '''
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        '''
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        return cls._second('-', u(cls._first('', value).strip().lower()))


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
