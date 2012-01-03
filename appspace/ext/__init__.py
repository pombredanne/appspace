# -*- coding: utf-8 -*-
'''appspace extensions'''

from .apps import on, __
from .services import service
from .descriptors import direct, factory, forward
from .classes import Client, Host, Master, Server, Synched

__all__ = [
    '__', 'Client', 'Host', 'Master', 'Server', 'Synched', 'factory', 'on',
    'forward', 'service', 'direct', 'remote',
]
