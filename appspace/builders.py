# -*- coding: utf-8 -*-
'''build appspaces'''

from __future__ import absolute_import

from operator import getitem, contains

from stuf.utils import lazy, selfname

from .utils import lru_cache
from .error import AppLookupError, NoAppError
from .core import AAppspace, ABranch, ANamespace
from .managers import Manager, appifies, global_appspace

__all__ = ['Branch', 'Namespace', 'Patterns', 'app', 'include', 'patterns']


def include(module):
    '''
    add branch appspace

    @param module: module import path
    '''
    return ('include', module)


def patterns(label, *args, **kw):
    '''
    configure appspace

    @param label: name of branch appspace
    @param *args: tuple of module paths or component inclusions
    '''
    return Factory(label, *args, **kw).build()


class Appspace(object):

    '''interface with appspace'''

    __slots__ = ['manager']

    appifies(AAppspace)

    def __init__(self, manager):
        '''
        @param manager: appspace manager
        '''
        self.manager = manager

    def __getattr__(self, label):
        try:
            return object.__getattribute__(self, label)
        except AttributeError:
            return self.__getitem__(label)

    @lru_cache()
    def __getitem__(self, label):
        try:
            return self.manager.get(label)
        except AppLookupError:
            raise NoAppError('%s' % label)

    def __call__(self, label, *args, **kw):
        result = getitem(self, label)
        try:
            return result(*args, **kw)
        except TypeError:
            return result

    def __contains__(self, label):
        return contains(self.manager, label)

    def __repr__(self):
        return self.manager.__repr__()


class Factory(object):

    '''factory for appspace'''

    def __init__(self, label, *args, **kw):
        '''
        @param label: label for manager
        '''
        # whether to use global manager instead of local manager
        self._global = kw.get('use_global', False)
        # object with manager configuration
        self._module = kw.get('module', 'appconf')
        # register apps in manager
        apper = self.manager.set
        # add applications
        for arg in args:
            apper(*arg)
        # add manager
        apper(label, Appspace(self.manager))

    def __repr__(self):
        return self.manager.__repr__()

    @lazy
    def manager(self):
        '''manager builder'''
        return global_appspace if self._global else Manager(self._module)

    def build(self):
        '''build manager'''
        return Appspace(self.manager)


class Patterns(object):

    '''patterns for manager configured in a class'''

    def __repr__(self):
        return str(self._gather())

    @classmethod
    def _gather(cls):
        this = list()
        tappend = this.append
        textend = this.extend
        # filters
        anamespace = ANamespace.implementedBy
        branch = ABranch.implementedBy
        for k, v in vars(cls).iteritems():
            # filter private and hidden
            if not k.startswith('_'):
                # handle namespace
                if anamespace(v):
                    textend(i for i in v.build())
                # handle branches
                elif branch(v):
                    textend(v.build())
                # handle anything else
                else:
                    tappend((k, v))
        return this

    @classmethod
    def settings(cls, appconf, required, defaults):
        conf = appconf.manager.settings
        # attach conf
        conf.required = required
        conf.defaults = defaults

    @classmethod
    def build(cls, required=None, defaults=None):
        '''
        build manager configuration from class

        @param required: required conf
        @param defaults: default conf
        '''
        this = list()
        tappend = this.append
        textend = this.extend
        # filters
        anamespace = ANamespace.implementedBy
        branch = ABranch.implementedBy
        for k, v in vars(cls).iteritems():
            # filter private and hidden
            if not k.startswith('_'):
                # handle namespace
                if anamespace(v):
                    textend(i for i in v.build())
                # handle branches
                elif branch(v):
                    textend(v.build())
                # handle anything else
                else:
                    tappend((k, v))
        # build configuration
        appconf = patterns(selfname(cls), *tuple(cls._gather()))
        if required is not None and defaults is not None:
            cls.settings(appconf, required, defaults)
        return appconf


class Branch(object):

    '''branch configuration class'''

    appifies(ABranch)

    @classmethod
    def build(cls):
        '''gather branch configuration'''
        return [
            (k, include(v)) for k, v in vars(cls).iteritems()
            if all([not k.startswith('_'), isinstance(v, basestring)])
        ]


class Namespace(object):

    '''configuration namespace'''

    appifies(ANamespace)

    @classmethod
    def _pack(cls, this, that):
        # build name
        return ('.'.join([selfname(cls), this]), that)

    @classmethod
    def build(cls):
        '''gather namespace configuration'''
        this = list()
        tappend = this.append
        textend = this.extend
        anamespace = ANamespace.implementedBy
        pack = cls._pack
        for k, v in vars(cls).iteritems():
            if not k.startswith('_'):
                # handle namespaces
                if anamespace(v):
                    textend(pack(*i) for i in v.build())
                else:
                    tappend(pack(k, v))
        return this


# global manager shortcut
app = Appspace(global_appspace)
