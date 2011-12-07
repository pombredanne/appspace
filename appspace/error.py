# -*- coding: utf-8 -*-
'''appspace exceptions'''

from zope.interface.interfaces import ComponentLookupError

# app lookup exception
AppLookupError = ComponentLookupError


class ConfigurationError(Exception):

    '''Appspace configuration exception'''


class NoAppError(Exception):

    '''No application found exception'''