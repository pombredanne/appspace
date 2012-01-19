# -*- coding: utf-8 -*-
'''building queue'''

from __future__ import absolute_import

from appspace.query import Queue as BaseQueue
from appspace.error import ConfigurationError, NoAppError

from stuf.utils import lazy

from .mixin import QueryMixin


class BuildQueue(QueryMixin, BaseQueue):

    '''appspace building queue'''

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            return super(BuildQueue, self).branch(label)
        # create new branch
        except NoAppError:
            new_appspace = self._manage_class
            self.manager.set(label, new_appspace)
            self.appendleft(new_appspace)
            return self
        raise ConfigurationError('invalid branch configuration')

    @lazy
    def builder(self):
        '''builder queue to attach to other apps'''
        return BuildQueue(self.manager)

    def set(self, app, label, branch=False):
        '''
        add application to appspace

        @param app: new application
        @param label: application label
        @param branch: branch label (default: False)
        '''
        # use branch manager
        if branch:
            manager = self.branch(self, branch).one().manager
        # use passed manager
        else:
            manager = self.manager
        # add to appspace
        manager.set(label, app)
        self.appendleft(app)
        return self


__all__ = ['BuildQueue']
