# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import absolute_import

from .classes import Delegated, HasTraits, Sync, Hosted
from .settings import RequiredSettings, DefaultSettings
from .query import __, Query, component, delegatable, delegated, on
from .builders import Branch, Patterns, Namespace, include, app, patterns
