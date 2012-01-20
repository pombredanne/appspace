# -*- coding: utf-8 -*-
'''extension keys'''

from __future__ import absolute_import

from appspace.keys import AppspaceKey


class AClient(AppspaceKey):

    '''client key'''


class AServer(AppspaceKey):

    '''server key'''


class AService(AppspaceKey):

    '''service key'''


__all__ = ('AClient', 'AServer', 'AService')
