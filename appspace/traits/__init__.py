# -*- coding: utf-8 -*-
'''
A lightweight Traits like module.

This is designed to provide a lightweight, simple, pure Python version of
many of the capabilities of enthought.traits.  This includes:

* Validation
* Type specification with defaults
* Static and dynamic notification
* Basic predefined types
* An API that is similar to enthought.traits

We don't support:

* Delegation
* Automatic GUI generation
* A full set of trait types.  Most importantly, we don't provide container
  traits (list, dict, tuple) that can trigger notifications if their
  contents change.
* API compatibility with enthought.traits

There are also some important difference in our design:

* enthought.traits does not validate default values.  We do.

We choose to create this module because we need these capabilities, but we need
them to be pure Python so they work in all Python implementations, including
Jython and IronPython.

Authors:

* Brian Granger
* Enthought, Inc. Some of the code in this file comes from enthought.traits
  and is licensed under the BSD license.  Also, many of the ideas also come
  from enthought.traits even though our implementation is very different.

Distributed under the terms of the BSD License. The full license is in
the file COPYING, distributed as part of this software.
'''

from .support import Meta
from .base import HasTraitsMixin, SynchedMixin
from .error import TraitError
from .trait_types.base import TraitType
from .trait_types.properties import (
    StringField, IntegerField, TextField, CharField, BooleanField, FloatField,
)
