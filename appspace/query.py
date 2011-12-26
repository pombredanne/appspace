# -*- coding: utf-8 -*-
'''query'''

from stuf.utils import setter

from .utils import getcls
from .core import AAppQuery, appifies
from .builders import Appspace, AppspaceManager, patterns, app


class AppQuery(list):

    '''appspace query'''

    appifies(AAppQuery)

    def __init__(self, appspace, *args):
        '''
        @param appspace: an appspace
        '''
        self.appspace = appspace
        list.__init__(self, args)

    def __call__(self, *args):
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

    def get(self, label, branch=''):
        '''
        get component from appspace

        @param label: label for branch appspace
        @param branch: branch to add component to
        '''
        return self(
            self.appspace[branch][label] if branch else self.appspace[label]
        )

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
