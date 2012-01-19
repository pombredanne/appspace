# -*- coding: utf-8 -*-
'''application composing'''

from __future__ import absolute_import

from inspect import ismodule

from .query import __
from .holders import Sync
from .decorators import on
from .queue import ComposerQueue
from .classes import Composed, Master, Synced

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_') and name != '__', ismodule(obj),
]))

del ismodule
