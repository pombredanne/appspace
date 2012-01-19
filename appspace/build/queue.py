# -*- coding: utf-8 -*-
'''build queue'''

from __future__ import absolute_import

from appspace.query import Queue as BaseQueue
from appspace.error import ConfigurationError, NoAppError

from .mixin import QueryMixin


class BuildQueue(QueryMixin, BaseQueue):

    '''appspace queued builder'''

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
            self._manager.set(label, new_appspace)
            self.appendleft(new_appspace)
            return self
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
            manager = self.branch(self, branch).one().manager
        # use passed manager
        else:
            manager = self._manager
        # add to appspace
        manager.set(label, app)
        self.appendleft(app)
        return self


__all__ = ['BuildQueue']
