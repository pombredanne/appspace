# -*- coding: utf-8 -*-
'''appspace extensions'''

from inspect import ismodule

from .apps import AppPatterns, on, __
from .core import Q, B, direct, factory
from .classes import Client, Server, Synced
from .settings import RequiredSettings, DefaultSettings
from .services import forward, remote, service, servicer

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_') and name != '__', ismodule(obj),
]))

del ismodule
