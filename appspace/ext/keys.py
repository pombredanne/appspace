# -*- coding: utf-8 -*-
'''appspace extension keys'''

from appspace.keys import AppspaceKey


class AClient(AppspaceKey):

    '''appspace client key'''


class AMaster(AppspaceKey):

    '''appspace master key'''


class AServer(AppspaceKey):

    '''appspace server key'''


class AService(AppspaceKey):

    '''appspace service'''


class AServiceManager(AppspaceKey):

    '''appspace service manager'''


class NoDefaultSpecified(object):

    '''no default'''

    def generate(self, klass):
        '''generator'''


class Undefined(object):

    '''undefined value'''


NoDefaultSpecified = NoDefaultSpecified()
Undefined = Undefined()

__all__ = [
    'AClient', 'AMaster', 'AServer', 'AService', 'AServiceManager',
    'NoDefaultSpecified', 'Undefined',
]
