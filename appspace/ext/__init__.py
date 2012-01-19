# -*- coding: utf-8 -*-
'''appspace extensions'''

from __future__ import absolute_import

from inspect import ismodule

from .queue import namedqueue
from .classes import ResetMixin
from .core import Manager, Composer
from .events import Event, EventManager
from .settings import DefaultSettings, RequiredSettings

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_') and name != '__', ismodule(obj),
]))

del ismodule
