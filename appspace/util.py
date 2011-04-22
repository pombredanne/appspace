'''tubing utilities'''

import os
import sys
import imp
import string
from keyword import kwlist
from functools import wraps
from collections import OrderedDict

import pkg_resources
from appspace.exception import ConfigurationError

# Illegal characters for Python names
_ichar = '()[]{}@,:.`=;+-*/%&|^><\'"#\\$?!~'
_reserve, _keywords = string.maketrans('', ''), frozenset(kwlist)
init_names = [
    '__init__%s' % x[0] for x in imp.get_suffixes()
    if x[0] and x[2] not in (imp.C_EXTENSION, imp.C_BUILTIN)
]

def lru_cache(maxsize=100):
    '''Least-recently-used cache decorator.

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used
    '''
    def decorating_function(func):
        cache = OrderedDict()   # order: least recent to most recent
        @wraps(func)
        def wrapper(*args, **kw):
            key = args
            if kw: key += tuple(sorted(kw.items()))
            try:
                result = cache.pop(key)
            except KeyError:
                result = func(*args, **kw)
                # purge least recently used cache entry
                if len(cache) >= maxsize: cache.popitem(0)
            cache[key] = result         # record recent use of this key
            return result
        return wrapper
    return decorating_function

def checkname(name):
    '''Ensures a string is a legal Python name.'''
    # Remove characters that are illegal in a Python name
    name = name.replace('.', '_').translate(_reserve, _ichar)
    # Add _ if value is a Python keyword
    if name in _keywords: return ''.join([name, '_'])
    return name

def caller_path(path, level=2):
    if not os.path.isabs(path):
        module = caller_module(level+1)
        prefix = package_path(module)
        path = os.path.join(prefix, path)
    return path

def caller_module(level=2, sys=sys):
    module_globals = sys._getframe(level).f_globals
    module_name = module_globals.get('__name__') or '__main__'
    module = sys.modules[module_name]
    return module

def caller_package(level=2, caller_module=caller_module):
    # caller_module in arglist for tests
    module = caller_module(level+1)
    f = getattr(module, '__file__', '')
    if (('__init__.py' in f) or ('__init__$py' in f)): # empty at >>>
        # Module is a package
        return module
    # Go up one level to get package
    package_name = module.__name__.rsplit('.', 1)[0]
    return sys.modules[package_name]

def package_name(pkg_or_module):
    '''If this function is passed a module, return the dotted Python
    package name of the package in which the module lives.  If this
    function is passed a package, return the dotted Python package
    name of the package itself.
    '''
    if pkg_or_module is None: return '__main__'
    pkg_filename = pkg_or_module.__file__
    pkg_name = pkg_or_module.__name__
    splitted = os.path.split(pkg_filename)
    # it's a package
    if splitted[-1] in init_names: return pkg_name
    return pkg_name.rsplit('.', 1)[0]

def package_of(pkg_or_module):
    '''Return the package of a module or return the package itself'''
    pkg_name = package_name(pkg_or_module)
    __import__(pkg_name)
    return sys.modules[pkg_name]

def package_path(package):
    # computing the abspath is actually kinda expensive so we memoize
    # the result
    prefix = getattr(package, '__abspath__', None)
    if prefix is None:
        prefix = pkg_resources.resource_filename(package.__name__, '') #@UndefinedVariable
        # pkg_resources doesn't care whether we feed it a package
        # name or a module name within the package, the result
        # will be the same: a directory name to the package itself
        try:
            package.__abspath__ = prefix
        except:
            # this is only an optimization, ignore any error
            pass
    return prefix


class _DottedNameResolver(object):

    def __init__(self, package):
        if package is None:
            self.package_name = None
            self.package = None
        else:
            if isinstance(package, basestring):
                try:
                    __import__(package)
                except ImportError:
                    raise ConfigurationError(
                        'The dotted name %r cannot be imported' % package
                    )
                package = sys.modules[package]
            self.package = package_of(package)
            self.package_name = self.package.__name__

    def _zope_dottedname_style(self, value):
        '''package.module.attr style'''
        module = self.package_name
        if not module:
            module = None
        if value == '.':
            if module is None:
                raise ConfigurationError(
                    'relative name %r irresolveable without package' % value
                )
            name = module.split('.')
        else:
            name = value.split('.')
            if not name[0]:
                if module is None:
                    raise ConfigurationError(
                        'relative name %r irresolveable without package' % value
                    )
                module = module.split('.')
                name.pop(0)
                while not name[0]:
                    module.pop()
                    name.pop(0)
                name = module + name
        used = name.pop(0)
        found = __import__(used)
        for n in name:
            used += '.' + n
            try:
                found = getattr(found, n)
            except AttributeError:
                __import__(used)
                found = getattr(found, n) # pragma: no cover
        return found

    def resolve(self, dotted):
        if isinstance(dotted, basestring):
            return self._zope_dottedname_style(dotted)
        return dotted


class reify(object):

    '''Put the result of a method which uses this (non-data)
    descriptor decorator in the instance dict after the first call,
    effectively replacing the decorator with an instance variable.
    '''

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None: return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


name_resolver = _DottedNameResolver(caller_package())