# -*- coding: utf-8 -*-
'''settings'''
# pylint: disable-msg=f0401

from stuf import frozenstuf
from stuf.utils import lazy_set, lazy

from zope.interface import implements as appifies

from .utils import ResetMixin, object_walk
from .keys import ASettings, ADefaultSettings, AInternalSettings, ANamespace


class AppspaceSettings(ResetMixin):

    '''appspace settings'''

    appifies(ASettings)

    def __init__(self, **kw):
        super(AppspaceSettings, self).__init__()
        self._main = dict(**kw)
        self._default = {}
        self._internal = {}

    @lazy_set
    def default(self):
        '''get default settings separately'''
        return frozenstuf(self._default)

    @default.setter
    def default(self, value):
        '''
        set default settings separately

        @param value: default settings
        '''
        if ADefaultSettings.implementedBy(value):
            self._default.clear()
            self.update_default(value)
        else:
            raise TypeError('invalid DefaultSettings')

    @lazy_set
    def internal(self):
        '''get internal settings separately'''
        return frozenstuf(self._default)

    @internal.setter
    def internal(self, value):
        '''
        set internal settings separately

        @param value: internal settings
        '''
        if AInternalSettings.implementedBy(value):
            self._internal.clear()
            self.update_internal(value)
        else:
            raise TypeError('invalid InternalSettings')

    @lazy
    def main(self):
        '''get main settings separately'''
        main = self._default.copy()
        main.update(self._main.copy())
        main.update(self._internal.copy())
        return frozenstuf(main)

    def get(self, key, default=None):
        if default is None:
            default = self._default.get(key)
        return self._main.get(key, default)

    def set(self, key, value):
        self._main[key] = value

    def update_default(self, settings):
        if ADefaultSettings.implementedBy(settings):
            self.reset()
            self._default.update(object_walk(settings))
        else:
            raise TypeError('invalid DefaultSettings')

    def update_internal(self, settings):
        if AInternalSettings.implementedBy(settings):
            self.reset()
            self._internal.update(object_walk(settings))
        else:
            raise TypeError('invalid InternalSettings')

    def update(self, *args, **kw):
        self._main.update(*args, **kw)


class DefaultSettings(object):

    '''default settings class'''

    appifies(ADefaultSettings)


class InternalSettings(object):

    '''internal settings class'''

    appifies(AInternalSettings)


class Namespace(object):

    '''configuration namespace'''

    appifies(ANamespace)
