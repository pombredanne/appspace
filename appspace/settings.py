# -*- coding: utf-8 -*-
# pylint: disable-msg=f0401
'''settings'''

from __future__ import absolute_import

from stuf import frozenstuf, stuf
from stuf.utils import deepget, lazy_set, lazy, setter

from zope.interface import implements as appifies

from .utils import ResetMixin, object_walk
from .keys import ASettings, ADefaultSettings, AInternalSettings


class AppspaceSettings(ResetMixin):

    '''appspace settings'''

    appifies(ASettings)

    def __init__(self, **kw):
        super(AppspaceSettings, self).__init__()
        self._main = stuf(**kw)
        self._default = stuf()
        self._internal = stuf()

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
        '''
        get value from settings

        @param key: key in settings
        @param default: default value
        '''
        default = deepget(self._default, key, default)
        return deepget(key, self._main, default)

    def set(self, key, value):
        '''
        set internal settings separately

        @param key: key in settings
        @param value: value to put in settings
        '''
        try:
            path, key = key.rsplit('.', 1)
            try:
                setter(deepget(self._main, key), value)
            except AttributeError:
                paths = path.spit('.')
                this = self._main
                for part in paths:
                    new = stuf()
                    this[part] = new
                    this = new
                this[key] = value
        except ValueError:
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
