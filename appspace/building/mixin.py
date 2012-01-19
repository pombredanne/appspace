# -*- coding: utf-8 -*-
'''building mixins'''

from __future__ import absolute_import

import uuid

from appspace.keys import apped
from appspace.managers import Manager


class QueryMixin(object):

    '''appspace builder'''

    @property
    def _manage_class(self):
        # manager class
        return Manager()

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
