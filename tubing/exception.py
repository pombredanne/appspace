'''tubing exceptions'''

from zope.component.interfaces import ComponentLookupError #@UnresolvedImport @UnusedImport


class ConfigurationError(Exception):
    pass


class NoAppError(Exception):
    pass