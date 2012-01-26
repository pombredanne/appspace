# -*- coding: utf-8 -*-
'''appspace exceptions'''

from __future__ import absolute_import

from .keys import AppLookupError, DoesNotApp

__all__ = (
    'AppLookupError', 'ConfigurationError', 'NoAppspaceError', 'NoAppError',
)


class ConfigurationError(Exception):

    '''appspace configuration exception'''


class NoAppspaceError(Exception):

    '''no appspace found error'''


class NoAppError(Exception):

    '''mo application found exception'''


AppLookupError = AppLookupError
DoesNotApp = DoesNotApp
