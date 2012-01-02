# -*- coding: utf-8 -*-
'''appspace extensions'''

__all__ = [
    '__', 'Client', 'Host', 'Server', 'Synched', 'local', 'forward', 'on',
    'service',
]

# extended appspace
from .query import __
from .classes import Client, Host, Server, Synched
from .descriptors import forward, local, on, service
