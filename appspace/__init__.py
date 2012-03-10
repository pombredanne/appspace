# -*- coding: utf-8 -*-
'''appspace'''

from inspect import ismodule

from stuf.six import items

from appspace.registry import Registry
from appspace.keys import NoAppError, AppLookupError
from appspace.builders import patterns, class_patterns
from appspace.spaces import Branch, Namespace, Patterns, include

__version__ = (0, 5, 1)
__all__ = sorted(name for name, obj in items(locals()) if not any([
    name.startswith('_'), ismodule(obj),
]))
del ismodule
