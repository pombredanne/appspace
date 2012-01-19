# -*- coding: utf-8 -*-
'''composing mixin'''

from __future__ import absolute_import

from appspace.ext import Manager, Composer
from appspace.error import ConfigurationError
from appspace.spaces import Patterns, patterns

from operator import attrgetter

from stuf.utils import lazy

from appspace.keys import appifies

from .holders import Sync
from .keys import ASynched


class ComposerMixin(object):

    '''composer mixin'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        super(ComposerMixin, self).__init__(appspace, *args, **kw)
        # appspace settings
        self._settings = self._space.manager.settings
        self._events = self._space.manager.events

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


@appifies(ASynched)
class SyncedMixin(object):

    '''composed object with synchronizing functionality'''

    _element = attrgetter('element')
    _syncer = Sync

    def __getitem__(self, key):
        return self._sync.current[key]

    def __setitem__(self, key, value):
        return self._sync.update_current({key: value})

    def __delitem__(self, key):
        return self._sync.delete(key)

    def __contains__(self, key):
        return key in self._sync

    def __iter__(self):
        for k, v in self._sync:
            yield k, v

    def __repr__(self):
        return str(dict(i for i in self._sync.public.iteritems()))

    @lazy
    def _sync(self):
        # synchronizing handler
        return self._syncer(self._element(self), **self._attrs)
