# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401
'''extension keys'''

from __future__ import absolute_import

from inspect import ismodule

from appspace.keys import AppspaceKey


class AClient(AppspaceKey):

    '''appspace client key'''

class AServer(AppspaceKey):

    '''appspace server key'''


class AService(AppspaceKey):

    '''appspace service'''


class AServiceManager(AppspaceKey):

    '''appspace service manager'''


__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
