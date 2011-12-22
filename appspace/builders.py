# -*- coding: utf-8 -*-
'''builders'''

from __future__ import absolute_import

from operator import getitem, contains

from stuf.utils import attr_or_item, lazy, selfname

from .utils import lru_cache
from .error import AppLookupError, NoAppError
from .keys import AAppspace, ABranch, ANamespace
from .states import AppspaceManager, appifies, global_appspace


def add_app(appspace, label, component, branch='', use_global=False):
    '''
    add new component to appspace

    @param appspace: existing appspace
    @param label: label of branch appspace
    @param component: new component
    @param branch: branch to add component to
    @param use_global: use global appspace (default: False)
    '''
    if use_global:
        appspace = app
    elif branch:
        appspace = add_branch(appspace, branch)
    appspace.appspace.set(label, component)


def add_branch(appspace, label, use_global=False):
    '''
    add new appspace to existing appspace

    @param appspace: existing appspace
    @param label: label of new appspace
    @param use_global: use global appspace (default: False)
    '''
    if label not in appspace and not use_global:
        new_appspace = Appspace(AppspaceManager())
        appspace.appspace.set(label, new_appspace)
        return new_appspace
    return appspace


def include(module_path):
    '''
    load a branch appspace

    @param module_path: module import path
    '''
    return ('include', module_path)


def patterns(label, *args, **kw):
    '''
    configuration for branch appspace

    @param label: name of branch appspace
    @param *args: tuple of module paths or component inclusions
    '''
    return AppspaceFactory(label, *args, **kw)()


class Appspace(object):

    '''appspace interface'''

    __slots__ = ['appspace']

    appifies(AAppspace)

    def __init__(self, appspace):
        '''
        initialize appspace

        @param appspace: configured appspace
        '''
        self.appspace = appspace

    def __getattr__(self, label):
        '''
        access component in appspace

        @param label: label of component in appspace
        '''
        return attr_or_item(self, label)

    @lru_cache()
    def __getitem__(self, label):
        '''
        access component in appspace

        @param label: label of component in appspace
        '''
        try:
            return self.appspace.get(label)
        except AppLookupError:
            raise NoAppError('%s' % label)

    def __call__(self, label, *args, **kw):
        '''
        pass arguments to component in appspace

        @param label: label of component in appspace
        '''
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

    '''appspace factory'''

    def __init__(self, label, *args, **kw):
        '''
        init

        @param label: label of appspace
        @param *args: tuple of module paths or component inclusions
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
        '''instantiate appspace interface'''
        return Appspace(self._appspace)

    @lazy
    def _appspace(self):
        '''provide appspace'''
        return global_appspace if self._glob else AppspaceManager(self._mod)


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
                    textend([pack(*i) for i in v.build()])
                else:
                    tappend(pack(k, v))
        return this


class Patterns(object):

    '''pattern class settings'''

    @classmethod
    def build(cls):
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
        return patterns(selfname(cls), *tuple(this))


# global appspace shortcut
app = Appspace(global_appspace)
