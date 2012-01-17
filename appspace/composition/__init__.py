# -*- coding: utf-8 -*-
'''composition'''

from __future__ import absolute_import

from inspect import ismodule

from .holders import Sync
from .classes import Synced
from .core import AppPatterns, on, __
from .settings import DefaultSettings, RequiredSettings

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_') and name != '__', ismodule(obj),
]))

del ismodule
