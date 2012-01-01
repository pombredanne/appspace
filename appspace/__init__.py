# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import absolute_import

__version__ = (0, 5, 0)

__all__ = [
    'RequiredSettings', 'DefaultSettings', 'Branch', 'Patterns', 'Namespace',
    'include', 'app', 'patterns',
    '__', 'Delegater', 'Delegate', 'HasTraits', 'Synched', 'Host', 'instance',
    'delegate', 'delegated', 'on'
]

from .settings import RequiredSettings, DefaultSettings
from .builders import Branch, Patterns, Namespace, include, app, patterns

# extended appspace
from .ext.query import __, Query
from .ext.classes import (
    Delegater, Delegate, HasTraits, Synched, Host, instance, delegate, on,
    delegated,
)
