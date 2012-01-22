# -*- coding: utf-8 -*-
'''building queue'''

from __future__ import absolute_import

from appspace.query import Queue
from appspace.error import NoAppError

from stuf.utils import lazy

from .mixin import QueryMixin


class BuildQueue(QueryMixin, Queue):

    '''appspace building queue'''

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        with self.sync():
            # fetch branch if exists...
            try:
                self.outgoing.append(self._qbranch(label))
            # create new branch
            except NoAppError:
                new_appspace = self._manage_class
                self.manager.set(label, new_appspace)
                self.outgoing.append(new_appspace)
        return self

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
        with self.sync():
            # use branch manager
            if branch:
                manager = self._qbranch(branch)
            # use passed manager
            else:
                manager = self.manager
            # add to appspace
            manager.set(label, app)
            self.outgoing.append(app)
        return self


__all__ = ['BuildQueue']
