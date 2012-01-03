# -*- coding: utf-8 -*-
'''appspace extensions'''

__all__ = [
    '__', 'Client', 'Host', 'Server', 'Synched', 'local', 'remote', 'on',
    'service',
]

from .apps import __
from .classes import Client, Host, Server, Synched
from .descriptors import remote, local, on, service
