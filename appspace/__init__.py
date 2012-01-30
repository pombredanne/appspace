# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import unicode_literals

from inspect import ismodule

from six import iteritems
from appspace.keys import NoAppError, AppLookupError
from appspace.builders import patterns, class_patterns
from appspace.spaces import Branch, Namespace, Patterns, include

__version__ = (0, 5, 0)


__all__ = sorted(name for name, obj in iteritems(locals()) if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
