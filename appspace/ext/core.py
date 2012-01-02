# -*- coding: utf-8 -*-
'''appspace extension keys'''

from appspace.core import AppspaceKey


class AClient(AppspaceKey):

    '''delegated app key'''


class AServer(AppspaceKey):

    '''delegatable app key'''


class NoDefaultSpecified(object):

    def generate(self, klass):
        pass


NoDefaultSpecified = NoDefaultSpecified()


class Undefined(object):
    pass


Undefined = Undefined()
