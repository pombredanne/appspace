# -*- coding: utf-8 -*-
'''building query'''

from __future__ import absolute_import

from stuf.utils import lazy

from appspace.query import Query
from appspace.error import ConfigurationError, NoAppError

from .mixin import QueryMixin


class BuildQuery(QueryMixin, Query):

    '''appspace building query'''

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            return super(BuildQuery, self).branch(label)
        # create new branch
        except NoAppError:
            new_appspace = self._manage_class
            self.manager.set(label, new_appspace)
            return new_appspace
        raise ConfigurationError('invalid branch configuration')

    @lazy
    def builder(self):
        '''builder to attach to other apps'''
        return BuildQuery(self.manager)

    def set(self, app, label, branch=False):
        '''
        add application to appspace

        @param app: new application
        @param label: application label
        @param branch: branch label (default: False)
        '''
        # use branch manager
        if branch:
            manager = self.branch(branch)
        # use passed manager
        else:
            manager = self.manager
        # add to appspace
        manager.set(label, app)
        return app


__all__ = ['BuildQuery']
