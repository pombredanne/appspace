# -*- coding: utf-8 -*-
'''appspace extensions'''

__all__ = [
    '__', 'Delegater', 'Delegate', 'HasTraits', 'Synched', 'Host', 'component',
    'delegate', 'delegated', 'on'
]

# extended appspace
from .query import __, Query
from .classes import (
    Delegater, Delegate, HasTraits, Synched, Host, component, delegate, on,
    delegated,
)
