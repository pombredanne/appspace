# -*- coding: utf-8 -*-
'''composing mixins'''

from __future__ import absolute_import

from appspace.ext import Manager, Composer
from appspace.error import ConfigurationError
from appspace.spaces import Patterns, patterns
from stuf.utils import lazy


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

    @lazy
    def compose(self, app):
        '''
        attach composer to another application

        @param app: application to attach composer to
        '''
        app._C = self.composer

    def bind(self, event, label, branch=False):
        '''
        bind get to event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.bind(event, self.get(label, branch).first())
        return self

    def lock(self):
        '''lock settings so they are read only except locals'''
        self._settings.lock()

    def register(self, model):
        '''
        register model in appspace

        @param model: class to be model
        '''
        self.query(model)
        self.build(model)
        # attach manager
        model.A = self._manager
        # attach manager settings
        model.S = self._settings.final
        return self

    def unbind(self, event, label, branch=False):
        '''
        unbind application from event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.unbind(event, self.get(label, branch).first())
        return self
