# -*- coding: utf-8 -*-
'''building double queue'''

from __future__ import absolute_import

from appspace.query import DoubleQueue as BaseQueue
from appspace.error import ConfigurationError, NoAppError

from stuf.utils import lazy

from .mixin import QueryMixin


class DoubleBuildQueue(QueryMixin, BaseQueue):

    '''appspace building queue'''

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            self.outgoing.append(super(DoubleBuildQueue, self).branch(label))
            return self
        # create new branch
        except NoAppError:
            new_appspace = self._manage_class
            self.manager.set(label, new_appspace)
            self.outgoing.append(new_appspace)
            return self
        raise ConfigurationError('invalid branch configuration')

    @lazy
    def builder(self):
        '''builder queue to attach to other apps'''
        return DoubleBuildQueue(self.manager)

    def set(self, app, label, branch=False):
        '''
        add application to appspace

        @param app: new application
        @param label: application label
        @param branch: branch label (default: False)
        '''
        # use branch manager
        if branch:
            manager = self.branch(self, branch).firstone().manager
        # use passed manager
        else:
            manager = self.manager
        # add to appspace
        manager.set(label, app)
        self.outgoing.append(app)
        return self


__all__ = ['BuildQueue']
