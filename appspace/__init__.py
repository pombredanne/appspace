# -*- coding: utf-8 -*-
'''appspace'''

from __future__ import absolute_import

from .ext.query import __, Query
from .settings import RequiredSettings, DefaultSettings
from .ext.utils import component, delegatable, delegated, on
from .ext.classes import Delegated, HasTraits, Synched, Hosted
from .builders import Branch, Patterns, Namespace, include, app, patterns
