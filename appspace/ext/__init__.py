# -*- coding: utf-8 -*-
'''appspace extensions'''

__all__ = [
    '__', 'Client', 'Server', 'Synched', 'service', 'on', 'local', 'forward',
]

# extended appspace
from .query import __
from .classes import Client, Server, Synched
from .descriptors import local, forward, service, on
