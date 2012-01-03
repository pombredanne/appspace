# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import absolute_import

__version__ = (0, 5, 0)

from .settings import RequiredSettings, DefaultSettings
from .builders import Branch, Patterns, Namespace, include, app, patterns

__all__ = [
    'RequiredSettings', 'DefaultSettings', 'Branch', 'Patterns', 'Namespace',
    'include', 'app', 'patterns',
]
