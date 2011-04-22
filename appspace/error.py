'''tubing exceptions'''

from zope.component.interfaces import ComponentLookupError

AppLookupError = ComponentLookupError


class ConfigurationError(Exception):
    pass


class NoAppError(Exception):
    pass