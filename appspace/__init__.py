# -*- coding: utf-8 -*-
'''application plumbing'''

from __future__ import absolute_import

from .utils import ResetMixin
from .constructs import delegater, component, delegate, delegatable, appspacer
from .builders import (
    Patterns, Branch, InternalSettings, DefaultSettings, Namespace, include,
    app, patterns, add_app, add_branch,
)
