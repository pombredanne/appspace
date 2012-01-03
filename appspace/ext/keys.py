# -*- coding: utf-8 -*-
'''appspace extension keys'''

from appspace.keys import AppspaceKey


class AClient(AppspaceKey):

    '''delegated app key'''


class AServer(AppspaceKey):

    '''delegatable app key'''


class AService(AppspaceKey):

    '''service'''


class AServiceManager(AppspaceKey):

    '''service manager'''


class NoDefaultSpecified(object):

    def generate(self, klass):
        pass


class Undefined(object):
    pass


NoDefaultSpecified = NoDefaultSpecified()
Undefined = Undefined()

__all__ = [
    'AClient', 'AServer', 'AService', 'AServiceManager',
    'NoDefaultSpecified', 'Undefined',
]
