# -*- coding: utf-8 -*-
'''extension keys'''

from __future__ import absolute_import

from inspect import ismodule

from appspace.keys import AppspaceKey


class AClient(AppspaceKey):

    '''appspace client key'''


class AServer(AppspaceKey):

    '''appspace server key'''


__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
