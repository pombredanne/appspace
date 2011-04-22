'''tubing exceptions'''

from zope.component.interfaces import ComponentLookupError

# app lookup exception
AppLookupError = ComponentLookupError


class ConfigurationError(Exception):

    '''Appspace configuration exception'''


class NoAppError(Exception):

    '''No application was found exception'''