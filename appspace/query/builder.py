# -*- coding: utf-8 -*-
# pylint: disable-msg=w0221
'''extension core classes'''

from __future__ import absolute_import

import uuid

from appspace.keys import apped
from appspace.error import ConfigurationError, NoAppError

from .query import Query
from appspace.managers import Manager
from appspace.builders import Appspace


class Builder(Query):

    '''appspace query'''

    @property
    def _manage_class(self):
        # manager class
        return Appspace(Manager())

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            return Query.branch(self, label)
        # create new branch
        except NoAppError:
            new_appspace = self._manage_class
            self._manager.set(label, new_appspace)
            self.appendleft(new_appspace)
            return self
        raise ConfigurationError('invalid branch configuration')

    @staticmethod
    def key(key, app):
        '''
        key an get

        @param key: key to key get
        @param get: get to key
        '''
        apped(app, key)
        return app

    def set(self, app, label, branch=False):
        '''
        add application to appspace

        @param app: new application
        @param label: application label
        @param branch: branch label (default: False)
        '''
        # use branch manager
        if branch:
            manager = Query.branch(self, branch).one().manager
        # use passed manager
        else:
            manager = self._manager
        # add to appspace
        manager.set(label, app)
        self.appendleft(app)
        return self

    @staticmethod
    def uuid():
        '''universal unique identifier'''
        return uuid.uuid4().hex.upper()


B = Builder
__all__ = ['B']
