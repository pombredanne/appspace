# -*- coding: utf-8 -*-
'''appspace'''

from appspace.registry import Registry
from appspace.keys import NoAppError, AppLookupError
from appspace.builders import patterns, class_patterns
from appspace.spaces import Branch, Namespace, Patterns, include

__version__ = (0, 5, 2)
