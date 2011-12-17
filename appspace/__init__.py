# -*- coding: utf-8 -*-
'''Python application plumbing'''

from __future__ import absolute_import

from .utils import ResetMixin
from .builders import (
    Patterns, Settings, InternalSettings, DefaultSettings, Include, include,
    patterns, add_app, add_branch, app,
)
from .constructs import delegater, component, delegate, delegatable, appspacer
