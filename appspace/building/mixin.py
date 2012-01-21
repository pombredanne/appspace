# -*- coding: utf-8 -*-
'''building mixins'''

from __future__ import absolute_import

import uuid
from threading import local

from appspace.keys import apped
from appspace.managers import Manager


class QueryMixin(local):

    '''appspace builder'''

    @property
    def _manage_class(self):
        # manager class
        return Manager()

    def build(self, app):
        '''
        add query to app

        @param app: app to add query to
        '''
        app._B = self.builder

    @staticmethod
    def key(key, app):
        '''
        key an get

        @param key: key to key get
        @param get: get to key
        '''
        apped(app, key)
        return app

    @staticmethod
    def uuid():
        '''universal unique identifier'''
        return uuid.uuid4().hex.upper()


__all__ = ['QueryMixin']
