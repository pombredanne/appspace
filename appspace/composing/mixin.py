# -*- coding: utf-8 -*-
'''composing mixins'''

from __future__ import absolute_import

from appspace.ext import Manager, Composer
from appspace.error import ConfigurationError
from appspace.spaces import Patterns, patterns


class ComposerMixin(object):

    '''composer mixin'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        super(ComposerMixin, self).__init__(appspace, *args, **kw)
        # appspace settings
        self._settings = self._manager.settings
        self._events = self._manager.events

    @property
    def _manage_class(self):
        # manager class
        return Manager()

    @classmethod
    def appspace(cls, pattern, required=None, defaults=None, *args, **kw):
        '''
        build new appspace

        @param pattern: pattern configuration class or appspace label
        @param required: required settings (default: None)
        @param defaults: default settings (default: None)
        @param *args: tuple of module paths or inclusions
        '''
        # from appspace configuration class...
        if issubclass(pattern, Patterns):
            return cls(pattern.build(required, defaults))
        # from label and arguments...
        elif isinstance(pattern, basestring) and args:
            return cls(Composer.settings(
                patterns(pattern, *args, **kw), required, defaults,
            ))
        raise ConfigurationError('patterns not found')

    def lock(self):
        '''lock settings so they are read only except locals'''
        self._settings.lock()
