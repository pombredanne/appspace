# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import absolute_import

from inspect import ismodule

from .builders import Branch, Patterns, Namespace, include, patterns

__version__ = (0, 5, 0)

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
