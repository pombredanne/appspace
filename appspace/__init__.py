# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import absolute_import

from .settings import RequiredSettings, DefaultSettings
from .ext.classes import Delegated, HasTraits, Synched, Hosted
from .ext.query import __, Query, component, delegatable, delegated, on
from .builders import Branch, Patterns, Namespace, include, app, patterns
