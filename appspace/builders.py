# -*- coding: utf-8 -*-
'''appspace builders'''

from __future__ import absolute_import

from operator import getitem, contains

from stuf.utils import attr_or_item, lazy, selfname

from .utils import lru_cache
from .error import AppLookupError, NoAppError
from .core import AAppspace, ABranch, ANamespace
from .states import AppspaceManager, appifies, global_appspace


def include(module):
    '''
    load configuration for a branch appspace

    @param module_path: module import path
    '''
    return ('include', module)


def patterns(label, *args, **kw):
    '''
    configuration for branch appspace

    @param label: name of branch appspace
    @param *args: tuple of module paths or component inclusions
    '''
    return AppspaceFactory(label, *args, **kw)()


class Appspace(object):

    '''interface with appspace'''

    __slots__ = ['appspace']

    appifies(AAppspace)

    def __init__(self, appspace):
        self.appspace = appspace

    def __getattr__(self, label):
        return attr_or_item(self, label)

    @lru_cache()
    def __getitem__(self, label):
        try:
            return self.appspace.get(label)
        except AppLookupError:
            raise NoAppError('%s' % label)

    def __call__(self, label, *args, **kw):
        result = getitem(self, label)
        try:
            return result(*args, **kw)
        except TypeError:
            return result

    def __contains__(self, label):
        return contains(self.appspace, label)

    def __repr__(self):
        return self.appspace.__repr__()


class AppspaceFactory(object):

    '''factory for appspace'''

    def __init__(self, label, *args, **kw):
        '''
        @param label: label for appspace
        '''
        # whether to use global appspace instead of local appspace
        self._glob = kw.get('use_global', False)
        self._mod = kw.get('mod', 'appconf')
        # register apps in appspace
        apper = self._appspace.set
        for arg in args:
            apper(*arg)
        apper(label, Appspace(self._appspace))

    def __call__(self):
        return Appspace(self._appspace)

    @lazy
    def _appspace(self):
        return global_appspace if self._glob else AppspaceManager(self._mod)


class Patterns(object):

    '''pattern class'''

    @classmethod
    def build(cls, required, defaults):
        this = list()
        tappend = this.append
        textend = this.extend
        anamespace = ANamespace.implementedBy
        branch = ABranch.implementedBy
        for k, v in vars(cls).iteritems():
            if not k.startswith('_'):
                if anamespace(v):
                    textend(i for i in v.build())
                elif branch(v):
                    textend(v.build())
                else:
                    tappend((k, v))
        appconf = patterns(selfname(cls), *tuple(this))
        appconf.appspace.settings.required = required
        appconf.appspace.settings.defaults = defaults
        return appconf


class Branch(object):

    '''branch configuration class'''

    appifies(ABranch)

    @classmethod
    def build(cls):
        return [
            (k, include(v)) for k, v in vars(cls).iteritems()
            if all([not k.startswith('_'), isinstance(v, basestring)])
        ]


class Namespace(object):

    '''configuration namespace'''

    appifies(ANamespace)

    @classmethod
    def _pack(cls, this, that):
        return ('.'.join([selfname(cls), this]), that)

    @classmethod
    def build(cls):
        this = list()
        tappend = this.append
        textend = this.extend
        anamespace = ANamespace.implementedBy
        pack = cls._pack
        for k, v in vars(cls).iteritems():
            if not k.startswith('_'):
                if anamespace(v):
                    textend(pack(*i) for i in v.build())
                else:
                    tappend(pack(k, v))
        return this


# global appspace shortcut
app = Appspace(global_appspace)
