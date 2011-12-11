# -*- coding: utf-8 -*-
## pylint: disable-msg=f0401
'''appspace exceptions'''

from __future__ import absolute_import, unicode_literals, print_function

from zope.interface.interfaces import ComponentLookupError

# app lookup exception
AppLookupError = ComponentLookupError


class ConfigurationError(Exception):

    '''Appspace configuration exception'''


class NoAppError(Exception):

    '''No application found exception'''