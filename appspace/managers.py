# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''application management'''

from __future__ import absolute_import

from .utils import lazy_import
from .registry import Registry

from .keys import AApp, ALazyApp, AManager, appifies


@appifies(AManager)
class Manager(Registry):

    '''state manager'''

    __slots__ = ('_key', '_label', '_settings')

    def __init__(self, label='appconf', ns='default'):
        '''
        init

        @param label: label for application configuration object
        @param ns: label for internal namespace
        '''
        super(Manager, self).__init__(AApp, ns)
        self._label = label

    def get(self, label):
        '''
        fetch get

        @param label: get or branch label
        '''
        get = super(Manager, self).get(label)
        if ALazyApp.providedBy(get):
            get = self.load(label, get.path)
        return get

    def load(self, label, module):
        '''
        load branch or get from appspace

        @param label: get or branch label
        @param module: module path
        '''
        # register branch appspace from include
        if isinstance(module, tuple):
            get = lazy_import(module[-1], self._label)
        # register get
        else:
            get = lazy_import(module)
        self.set(label, get)
        return get

    def set(self, label, get):
        '''
        register branch or get in appspace

        @param label: appspace label
        @param get: get to add to appspace
        '''
        if isinstance(get, (basestring, tuple)):
            get = LazyApp(get)
        super(Manager, self).set(label, get)


@appifies(ALazyApp)
class LazyApp(object):

    '''lazy get loader'''

    __slots__ = ['path']

    def __init__(self, path):
        '''
        init

        @param path: path to component module
        '''
        self.path = path

    def __repr__(self):
        return 'get@{path}'.format(path=self.path)


__all__ = ('Manager', 'LazyApp')
