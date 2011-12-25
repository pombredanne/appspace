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

Notes
-----
Our implementation of traits is based on Python's descriptor prototol. This
class is the base class for all such descriptors. The only magic we use is
a custom metaclass for the main :class:`HasTraits` class that does the
following:

1. Sets the :attr:`name` attribute of every :class:`TraitType` instance in
   the class dict to the name of the attribute.
2. Sets the :attr:`this_class` attribute of every :class:`TraitType`
   instance in the class dict to the *class* that declared the trait. This
   is used by the :class:`This` trait to allow subclasses to accept
   superclasses for :class:`This` values.

Authors:

* Brian Granger
* Enthought, Inc. Some of the code in this file comes from enthought.traits
  and is licensed under the BSD license.  Also, many of the ideas also come
  from enthought.traits even though our implementation is very different.

Distributed under the terms of the BSD License. The full license is in
the file COPYING, distributed as part of this software.
'''

__all__ = [
    'TraitType', 'Bytes', 'CBytes', 'CUnicode', 'CheckedUnicode', 'List',
    'Container', 'CaselessStrEnum', 'Any', 'Tuple', 'Dict', 'ObjectName',
    'DottedObjectName', 'This', 'Instance', 'Type', 'Bool', 'CBool', 'Int',
    'Unicode', 'Undefined', 'component', 'delegatable', 'delegate', 'on',
    'lazy_component',
]

from .core import TraitType, Undefined
from .base import component, delegatable, delegate, on
from .containers import (
    List, Container, CaselessStrEnum, Enum, Any, Tuple, Dict
)
from .lang import DottedObjectName, Instance, ObjectName, This, Type
from .strings import Bytes, CBytes, CUnicode, CheckedUnicode, Unicode
from .numbers import (
    Bool, CBool, CInt, CLong, CFloat, CComplex, Complex, Float, Int, Integer,
    Long,
)
