# -*- coding: utf-8 -*-
'''extension keys'''

from __future__ import absolute_import

from appspace.keys import AppspaceKey


class AClient(AppspaceKey):

    '''appspace client key'''


class AServer(AppspaceKey):

    '''appspace server key'''


__all__ = ('AClient', 'AServer')
