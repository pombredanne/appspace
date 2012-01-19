# -*- coding: utf-8 -*-
'''extension core classes'''

from __future__ import absolute_import

from appspace.error import ConfigurationError, NoAppError

from appspace.query import Q

from .mixin import QueryMixin


class Build(QueryMixin, Q):

    '''appspace builder'''

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            return super(Build, self).branch(label)
        # create new branch
        except NoAppError:
            new_appspace = self._manage_class
            self._manager.set(label, new_appspace)
            return new_appspace
        raise ConfigurationError('invalid branch configuration')

    def set(self, app, label, branch=False):
        '''
        add application to appspace

        @param app: new application
        @param label: application label
        @param branch: branch label (default: False)
        '''
        # use branch manager
        if branch:
            manager = self.branch(self, branch).manager
        # use passed manager
        else:
            manager = self._manager
        # add to appspace
        manager.set(label, app)
        return app


B = Build
__all__ = ['B']
