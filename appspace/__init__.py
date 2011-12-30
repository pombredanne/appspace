# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import absolute_import

__version__ = (0, 5, 0)

# core appspace
from .settings import RequiredSettings, DefaultSettings
from .builders import Branch, Patterns, Namespace, include, app, patterns

# extended appspace
from .ext.query import __, Query
from .ext.utils import component, delegatable, delegated, on
from .ext.classes import Delegated, HasTraits, Synched, Hosted
