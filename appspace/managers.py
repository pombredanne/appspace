# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001
'''appspace management'''

import re
import unicodedata

from appspace.utils import lazy_import
from appspace.registry import Registry
from appspace.six import string_types, u
from appspace.keys import AApp, ALazyApp, AManager, AppLookupError, appifies

__all__ = ('LazyApp', 'Manager')


@appifies(AManager)
class Manager(Registry):

    '''state manager'''

    __slots__ = ('_key', '_label', '_ns', '_first', '_second')

    _first = re.compile('[^\w\s-]').sub
    _second = re.compile('[-\s]+').sub

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(Manager, self).__init__(label, ns, AApp)

    def get(self, label):
        '''
        fetch app

        @param label: get or branch label
        '''
        key = self._key
        app = self.lookup1(key, key, label)
        if app is None:
            raise AppLookupError(app, label)
        if ALazyApp.providedBy(app):
            app = self.load(label, app.path)
        return app

    def load(self, label, module):
        '''
        load branch or get from appspace

        @param label: get or branch label
        @param module: module path
        '''
        # register branch appspace from include
        if isinstance(module, tuple):
            app = lazy_import(module[-1], self._label)
        # register get
        else:
            app = lazy_import(module)
        key = self._key
        self.register([key], key, label, app)
        return app

    def set(self, label, app):
        '''
        register branch or get in appspace

        @param label: appspace label
        @param get: get to add to appspace
        '''
        if isinstance(app, (string_types, tuple)):
            app = LazyApp(app)
        key = self._key
        self.register([key], key, label, app)
        return app

    @classmethod
    def slugify(cls, value):
        '''
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        '''
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        return cls._second('-', u(cls._first('', value).strip().lower()))


@appifies(ALazyApp)
class LazyApp(object):

    '''lazy get loader'''

    __slots__ = ['path']

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'app@{path}'.format(path=self.path)


iskeyed = Manager.iskeyed
