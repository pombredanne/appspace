# -*- coding: utf-8 -*-
'''Python application plumbing'''

from __future__ import absolute_import

from .util import lazy, lazy_class
from .builder import include, patterns, add_app, add_branch, app
from .constructs import (
    Delegated, class_component, delegate, delegated, instance_component,
)