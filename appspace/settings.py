# -*- coding: utf-8 -*-
'''appspace settings'''

from __future__ import absolute_import

from stuf import defaultstuf, frozenstuf, stuf
from stuf.utils import deepget, lazy, lazy_set, setter

from .utils import object_walk
from .containers import ResetMixin
from .core import ASettings, ADefaultSettings, ARequiredSettings, appifies


class Settings(ResetMixin):

    '''appspace settings'''

    appifies(ASettings)

    def __init__(self):
        super(Settings, self).__init__()
        # default settings
        self._default = stuf()
        # delegates settings
        self._delegates = defaultstuf(set)
        # final settings
        self._final = stuf()
        # local settings
        self._local = defaultstuf(set)
        # required settings
        self._required = stuf()

    def __repr__(self, *args, **kwargs):
        return str(self._final)

    @lazy
    def d(self):
        '''get default settings separately'''
        return self.defaults

    @lazy_set
    def defaults(self):
        '''get default settings separately'''
        return frozenstuf(self._default)

    @defaults.setter
    def defaults(self, value):
        '''
        set default settings separately

        @param value: default settings
        '''
        if ADefaultSettings.implementedBy(value):
            self._default.clear()
            self.update_default(value)
        else:
            raise TypeError('invalid DefaultSettings')

    @lazy
    def delegates(self):
        '''get delegates separately'''
        return self._delegates

    @lazy
    def local(self):
        return self._local

    @lazy
    def r(self):
        '''get required settings separately'''
        return self.required

    @lazy_set
    def required(self):
        '''get required settings separately'''
        return frozenstuf(self._required)

    @required.setter
    def required(self, value):
        '''
        set required settings separately

        @param value: required settings
        '''
        if ARequiredSettings.implementedBy(value):
            self._required.clear()
            self.update_required(value)
        else:
            raise TypeError('invalid RequiredSettings')

    @lazy
    def f(self):
        '''finalized settings'''
        return self.final

    @lazy
    def final(self):
        '''finalized settings'''
        final = self._default.copy()
        final.update(self._final.copy())
        final.update(self._required.copy())
        return frozenstuf(final)

    def get(self, key, default=None):
        '''
        get value from settings

        @param key: key in settings
        @param default: default value (default: None)
        '''
        return deepget(self._final, key, default)

    def set(self, key, value):
        '''
        set required settings separately

        @param key: key in settings
        @param value: value to put in settings
        '''
        try:
            path, key = key.rsplit('.', 1)
            try:
                setter(deepget(self._final, key), key, value)
            except AttributeError:
                paths = path.split('.')
                this = self._final
                for part in paths:
                    new = stuf()
                    this[part] = new
                    this = new
                this[key] = value
        except ValueError:
            self._final[key] = value
        self.reset()

    def update(self, *args, **kw):
        '''
        update final setting
        '''
        self._final.update(*args, **kw)
        self.reset()

    def update_default(self, settings):
        '''
        update default settings

        @param settings: new settings
        '''
        if ADefaultSettings.implementedBy(settings):
            self.reset()
            self._default.update(object_walk(settings))
        else:
            raise TypeError('invalid DefaultSettings')

    def update_required(self, settings):
        '''
        update required settings

        @param settings: new settings
        '''
        if ARequiredSettings.implementedBy(settings):
            self.reset()
            self._required.update(object_walk(settings))
        else:
            raise TypeError('invalid RequiredSettings')


class DefaultSettings(object):

    '''default settings class'''

    appifies(ADefaultSettings)


class RequiredSettings(object):

    '''required settings class'''

    appifies(ARequiredSettings)
