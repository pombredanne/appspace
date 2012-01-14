# -*- coding: utf-8 -*-
'''exceptions'''

from __future__ import absolute_import

from .keys import AppLookupError

AppLookupError = AppLookupError


class ConfigurationError(Exception):

    '''appspace configuration exception'''


class NoAppspaceError(Exception):

    '''no appspace found error'''


class NoAppError(Exception):

    '''mo application found exception'''


__all__ = (
    'AppLookupError', 'ConfigurationError', 'NoAppspaceError', 'NoAppError',
)
