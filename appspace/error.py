# -*- coding: utf-8 -*-
# pylint: disable-msg=w0611
'''appspace exceptions'''

from __future__ import absolute_import

from .core import AppLookupError  # @UnusedImport


class ConfigurationError(Exception):

    '''Appspace configuration exception'''


class NoAppError(Exception):

    '''No application found exception'''


class TraitError(Exception):

    '''trait error'''
