# -*- coding: utf-8 -*-
'''appspace management'''

import re
from unicodedata import normalize

from stuf.six import u

from appspace.registry import Registry, StrictRegistry
from appspace.keys import AManager, ANamespace, AppLookupError, appifies

__all__ = ('Manager', 'StrictManager')


class ManagerMixin(object):

    '''state manager'''

    _first = staticmethod(re.compile('[^\w\s-]').sub)
    _second = staticmethod(re.compile('[-\s]+').sub)

    def apply(self, label, key=False, *args, **kw):
        '''
        invoke appspaced call

        @param label: appspaced call
        @param key: key label (default: False)
        '''
        return self.get(label, key)(*args, **kw)

    def get(self, label, key=False):
        '''
        get thing from appspace

        @param label: appspaced thing label
        @param key: `appspace` key (default: False)
        '''
        # use internal key if key label == internal key
        key = self._key if key == self._root else self.namespace(key)
        app = self.lookup1(key, key, label)
        if app is None:
            raise AppLookupError(app, label)
        return self._unlazy(label, key, app)

    def namespace(self, label):
        '''
        fetch key

        @param label: `appspace` key label
        '''
        this = self.lookup1(ANamespace, ANamespace, label)
        if this is None:
            raise AppLookupError(this, label)
        return this

    def set(self, thing=False, label=False, key=False):
        '''
        add thing to `appspace`

        @param thing: new `appspace` thing (default: False)
        @param label: new `appspace` thing label (default: False)
        @param key: key label (default: False)
        '''
        thing = self._lazy(thing)
        key = self.namespace(key) if key else self._key
        self.register([key], key, self.safename(label), thing)
        return thing

    @classmethod
    def slugify(cls, value):
        '''
        normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens
        '''
        return cls._second('-', u(cls._first(
            '', normalize('NFKD', value).encode('ascii', 'ignore')
        ).strip().lower()))


@appifies(AManager)
class Manager(ManagerMixin, Registry):

    '''state manager'''

    __slots__ = ('_current', '_root', '_key')


@appifies(AManager)
class StrictManager(ManagerMixin, StrictRegistry):

    '''strict manager'''

    __slots__ = ('_current', '_root', '_key')


keyed = Manager.keyed
