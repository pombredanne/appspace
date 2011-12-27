# -*- coding: utf-8 -*-
'''appspace exceptions'''

from __future__ import absolute_import

from .core import AppLookupError


class ConfigurationError(AppLookupError):

    '''appspace configuration exception'''


class NoAppspaceError(AppLookupError):

    '''no appspace found error'''


class NoAppError(AppLookupError):

    '''mo application found exception'''


class TraitError(AppLookupError):

    '''trait error'''
