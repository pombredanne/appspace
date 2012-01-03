# -*- coding: utf-8 -*-
'''appspace extensions'''

__all__ = [
    '__', 'Client', 'Host', 'Server', 'Synched', 'factory', 'forward', 'on',
    'service', 'direct',
]

from .apps import on, __
from .services import service
from .descriptors import direct, factory, forward
from .classes import Client, Host, Server, Synched
