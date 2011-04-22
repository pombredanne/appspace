'''tubing exceptions'''

from zope.component.interfaces import ComponentLookupError as AppLookupError  #@UnusedImport


class ConfigurationError(Exception):
    pass


class NoAppError(Exception):
    pass