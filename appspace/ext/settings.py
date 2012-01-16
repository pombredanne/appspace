# -*- coding: utf-8 -*-
'''extension settings management'''

from __future__ import absolute_import

from stuf import defaultstuf, frozenstuf, stuf
from stuf.utils import deepget, lazy, lazy_set, setter

from appspace.keys import appifies
from appspace.utils import ResetMixin, object_walk

from .keys import ADefaultSettings, ARequiredSettings, ASettings


class lock_set(lazy_set):

    '''lazy assign attributes with a custom setter'''

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if instance._locked:
            return setter(instance, self.name, self.method(instance))
        return self.method(instance)


@appifies(ASettings)
class Settings(ResetMixin):

    '''settings management'''

    def __init__(self):
        super(Settings, self).__init__()
        # default settings
        self._default = stuf()
        # final settings
        self._final = stuf()
        # factory settings
        self._local = defaultstuf(set)
        # required settings
        self._required = stuf()
        # turn off lock initially
        self._locked = False

    def __repr__(self, *args, **kwargs):
        return str(self._final)

    @lock_set
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
            raise TypeError('invalid default settings')

    @lock_set
    def final(self):
        '''finalized settings'''
        final = self._default.copy()
        final.update(self._final.copy())
        final.update(self._required.copy())
        return frozenstuf(final)

    @lazy
    def local(self):
        '''return local settings'''
        return self._local

    @lock_set
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
            raise TypeError('invalid required settings')

    def get(self, key, default=None):
        '''
        get value from settings

        @param key: key in settings
        @param default: default value (default: None)
        '''
        return deepget(self._final, key, default)

    def lock(self):
        '''lock settings'''
        self._locked = True

    def set(self, key, value):
        '''
        set final settings separately

        @param key: key in settings
        @param value: value to put in settings
        '''
        try:
            path, key = key.rsplit('.', 1)
            try:
                setattr(deepget(self._final, key), key, value)
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

    def update(self, *args, **kw):
        '''update final setting'''
        self._final.update(*args, **kw)

    def update_default(self, settings):
        '''
        update default settings

        @param settings: new settings
        '''
        if ADefaultSettings.implementedBy(settings):
            self._default.update(object_walk(settings))
        else:
            raise TypeError('invalid default settings')

    def update_required(self, settings):
        '''
        update required settings

        @param settings: new settings
        '''
        if ARequiredSettings.implementedBy(settings):
            self._required.update(object_walk(settings))
        else:
            raise TypeError('invalid required settings')


@appifies(ADefaultSettings)
class DefaultSettings(object):

    '''default settings'''


@appifies(ARequiredSettings)
class RequiredSettings(object):

    '''required settings'''


__all__ = ('DefaultSettings', 'RequiredSettings', 'Settings')
