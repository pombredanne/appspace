# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002,w0221
'''composition core'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.spaces import Patterns
from appspace.managers import Manager as BaseManager

from .settings import Settings
from .events import EventManager
from .keys import AEventManager, ASettings


class Manager(BaseManager):

    '''state manager'''

    __slots__ = ('_key', '_label', '_settings', 'events', 'settings')

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(Manager, self).__init__(label, ns)
        self.ez_register(ASettings, 'default', Settings)
        self.ez_register(AEventManager, 'default', EventManager)

    @lazy
    def events(self):
        '''get appspace events manager'''
        return self.ez_lookup(AEventManager, self._settings)(self)

    @lazy
    def settings(self):
        '''get appspace settings'''
        return self.ez_lookup(ASettings, self._settings)()


class Composer(Patterns):

    '''patterns for manager configured by class'''

    _manager = Manager

    @classmethod
    def build(cls, required=None, defaults=None):
        '''
        build manager configuration from class

        @param required: required settings
        @param defaults: default settings
        '''
        appconf = super(Composer, cls).build()
        if required is not None and defaults is not None:
            cls.settings(appconf, required, defaults)
        return appconf

    @classmethod
    def settings(cls, manager, required, defaults):
        '''
        attach settings to class

        @param required: required settings
        @param defaults: default settings
        '''
        manager.settings.required = required
        manager.settings.defaults = defaults


__all__ = ('Manager', 'Composer')
