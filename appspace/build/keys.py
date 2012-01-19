# -*- coding: utf-8 -*-
'''query keys'''

from __future__ import absolute_import

from inspect import ismodule

from appspace.keys import AppspaceKey


class ABuilt(AppspaceKey):

    '''built query object key'''


class ABuiltQueue(AppspaceKey):

    '''built queued and queried object key'''


__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
