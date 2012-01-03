# -*- coding: utf-8 -*-
'''appspace conf'''

from __future__ import absolute_import

from stuf import defaultstuf, frozenstuf, stuf
from stuf.utils import deepget, lazy, lazy_set, setter

from .utils import ResetMixin, object_walk
from .keys import ASettings, ADefaultSettings, ARequiredSettings, appifies

__all__ = ['DefaultSettings', 'RequiredSettings', 'Settings']


class Settings(ResetMixin):

    '''appspace conf'''

    appifies(ASettings)

    def __init__(self):
        super(Settings, self).__init__()
        # default conf
        self._default = stuf()
        # final conf
        self._final = stuf()
        # factory conf
        self._local = defaultstuf(set)
        # required conf
        self._required = stuf()

    def __repr__(self, *args, **kwargs):
        return str(self._final)

    @lazy_set
    def defaults(self):
        '''get default conf separately'''
        return frozenstuf(self._default)

    @defaults.setter
    def defaults(self, value):
        '''
        set default conf separately

        @param value: default conf
        '''
        if ADefaultSettings.implementedBy(value):
            self._default.clear()
            self.update_default(value)
        else:
            raise TypeError('invalid DefaultSettings')

    @lazy
    def final(self):
        '''finalized conf'''
        final = self._default.copy()
        final.update(self._final.copy())
        final.update(self._required.copy())
        return frozenstuf(final)

    @lazy
    def factory(self):
        '''return factory settings'''
        return self._local

    @lazy_set
    def required(self):
        '''get required conf separately'''
        return frozenstuf(self._required)

    @required.setter
    def required(self, value):
        '''
        set required conf separately

        @param value: required conf
        '''
        if ARequiredSettings.implementedBy(value):
            self._required.clear()
            self.update_required(value)
        else:
            raise TypeError('invalid RequiredSettings')

    def get(self, key, default=None):
        '''
        get value from conf

        @param key: key in conf
        @param default: default value (default: None)
        '''
        return deepget(self._final, key, default)

    def set(self, key, value):
        '''
        set required conf separately

        @param key: key in conf
        @param value: value to put in conf
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

    def update_default(self, conf):
        '''
        update default conf

        @param conf: new conf
        '''
        if ADefaultSettings.implementedBy(conf):
            self.reset()
            self._default.update(object_walk(conf))
        else:
            raise TypeError('invalid DefaultSettings')

    def update_required(self, conf):
        '''
        update required conf

        @param conf: new conf
        '''
        if ARequiredSettings.implementedBy(conf):
            self.reset()
            self._required.update(object_walk(conf))
        else:
            raise TypeError('invalid RequiredSettings')


class DefaultSettings(object):

    '''default conf class'''

    appifies(ADefaultSettings)


class RequiredSettings(object):

    '''required conf class'''

    appifies(ARequiredSettings)
