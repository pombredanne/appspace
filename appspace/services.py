# -*- coding: utf-8 -*-
# pylint: disable-msg=f0401
'''services'''

from __future__ import absolute_import

from zope.interface import implements as appifies

from .keys import ALazyApp


class LazyApp(object):

    '''lazy component loader'''

    appifies(ALazyApp)
    __slots__ = ['path']

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'component@{path}'.format(path=self.path)
