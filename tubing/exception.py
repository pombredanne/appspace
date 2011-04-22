'''tubing exceptions'''

from zope.component.interfaces import ComponentLookupError as AppLookupError #@UnresolvedImport @UnusedImport


class ConfigurationError(Exception):
    pass


class NoAppError(Exception):
    pass