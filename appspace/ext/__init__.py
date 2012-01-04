# -*- coding: utf-8 -*-
'''appspace extensions'''

from .apps import on, __
from .core import Q, B, direct, factory
from .services import forward, remote, service, servicer
from .classes import Client, Host, Master, Server, Synched

__all__ = [
    '__', 'Q', 'B', 'Client', 'Host', 'Master', 'Server', 'Synched', 'factory',
    'on', 'forward', 'service', 'direct', 'remote', 'servicer',
]
