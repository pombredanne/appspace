# -*- coding: utf-8 -*-
'''query'''

from inspect import ismethod

from stuf import stuf
from stuf.utils import setter, instance_or_class, get_or_default

from .core import AAppQuery, appifies
from .utils import getcls, itermembers, isrelated, lazy_import
from .builders import Appspace, AppspaceManager, patterns, app


class AppQuery(list):

    '''appspace query'''

    appifies(AAppQuery)

    def __init__(self, appspace, *args):
        '''
        @param appspace: an appspace
        '''
        self.appspace = get_or_default(appspace, 'a', appspace)
        list.__init__(self, args)

    def __call__(self, *args):
        '''
        @param appspace: an appspace
        '''
        return getcls(self)(self.appspace, *args)

    def app(self, label, component, branch='', use_global=False):
        '''
        add new component to appspace

        @param label: label for branch appspace
        @param component: new component
        @param branch: branch to add component to
        @param use_global: use global appspace (default: False)
        '''
        appspace = self.appspace
        if use_global:
            appspace = app
        elif branch:
            appspace = self.add_branch(branch)
        appspace.appspace.set(label, component)
        return self

    def branch(self, label, use_global=False):
        '''
        add new appspace to existing appspace

        @param label: label of new appspace
        @param use_global: use global appspace (default: False)
        '''
        appspace = self.appspace
        if label not in appspace and not use_global:
            new_appspace = Appspace(AppspaceManager())
            appspace.appspace.set(label, new_appspace)
            return new_appspace
        return self

    def build(self, pattern_class, required, defaults):
        '''
        build new appspace

        @param required: required settings
        @param defaults: default settings
        '''
        return self(pattern_class.build(required, defaults))

    @classmethod
    def class_space(cls, desc, this, that):
        '''
        get appspace attached to class

        @param this: an instance
        @param that: the instance's class
        '''
        if not desc._appspace:
            appspace = instance_or_class('a', this, that)
            if appspace is None:
                appspace = this.a = lazy_import('appspace.builder.app')
            desc._appspace = appspace
        return cls(desc._appspace)

    @staticmethod
    def filter_members(this, that):
        '''
        filter members of an object by class

        @param this: an instance
        @param that: a class
        '''
        return stuf(
            (k, v) for k, v in itermembers(this, ismethod)
            if isrelated(v, that)
        )

    def get(self, label, branch=''):
        '''
        get component from appspace

        @param label: label for branch appspace
        @param branch: branch to add component to
        '''
        return self(
            self.appspace[branch][label] if branch else self.appspace[label]
        )

    def localize(self, this):
        '''add local settings to appspace settings'''
        local = self.appspace.s.local
        lid = self.id(this)
        local[lid] = dict(
          dict((k, v) for k, v in vars(m).iteritems() if not k.startswith('_'))
          for m in get_or_default(this, '_metas', []) + [this.Meta]
        )
        return local[lid]

    @classmethod
    def id(cls, this):
        return '_'.join([this.__module__, this(self)])

    def patterns(self, label, *args, **kw):
        '''
        configuration for branch appspace

        @param label: name of branch appspace
        @param *args: tuple of module paths or component inclusions
        '''
        return self(patterns(label, *args, **kw))

    def register(self, klass):
        '''
        add appspace to class

        @param appspace: appspace to add
        '''
        setter(klass, 'a', self.appspace)
        setter(klass, 's', self.appspace.settings)
        return self


# shortcut
__ = AppQuery
