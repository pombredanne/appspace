# -*- coding: utf-8 -*-
'''services'''

from __future__ import absolute_import

from inspect import ismodule

from .query import S
from .classes import Client, Server
from .decorators import forward, remote, service, servicer

__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
