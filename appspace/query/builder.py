# -*- coding: utf-8 -*-
'''building query'''

from __future__ import absolute_import

import uuid

from appspace.query import Query
from appspace.keys import apped
from appspace.managers import Manager
from appspace.error import ConfigurationError, NoAppError


class Builder(Query):

    '''appspace building query'''

    @property
    def _manage_class(self):
        '''manager class'''
        return Manager()

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            return super(Builder, self).branch(label)
        # ...or create new branch
        except NoAppError:
            new_appspace = self._manage_class
            self.manager.set(label, new_appspace)
            return new_appspace
        raise ConfigurationError('invalid branch configuration')

    def build(self, app):
        '''
        add query to app

        @param app: app to add query to
        '''
        app._BQ = self.builder

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
            manager = self.branch(branch)
        # use passed manager
        else:
            manager = self.manager
        # add to appspace
        manager.set(label, app)
        return app

    @staticmethod
    def uuid():
        '''universal unique identifier'''
        return uuid.uuid4().hex.upper()


__all__ = ['BuildQuery']
