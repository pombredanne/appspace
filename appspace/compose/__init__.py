# -*- coding: utf-8 -*-
'''appspace composing'''

from __future__ import absolute_import

from inspect import ismodule

from .holders import Sync
from .query import ComposerQuery
from .queue import ComposerQueue
from .classes import Composed, Master, Synced
from .decorators import class_defer, direct, defer, factory, on

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_') and name != '__', ismodule(obj),
]))

del ismodule
