# -*- coding: utf-8 -*-

import re
import sys
import inspect
from types import InstanceType, ClassType

from stuf.utils import clsname

from appspace.traits.error import TraitError
from appspace.utils import lazy_import, class_of


from .base import TraitType

ClassTypes = (ClassType, type)


class ClassBasedTraitType(TraitType):

    '''A trait with error reporting for Type, Instance and This.'''

    def error(self, this, value):
        kind = type(value)
        if kind is InstanceType:
            msg = 'class %s' % clsname(value)
        else:
            msg = '%s (i.e. %s)' % (str(kind)[1:-1], repr(value))
        if this is not None:
            e = '%s trait of %s instance must be %s but value %s specified' % (
                self.name, class_of(this), self.info(), msg
            )
        else:
            e = 'the %s trait must be %s, but a value of %r was specified' % (
                self.name, self.info(), msg
            )
        raise TraitError(e)


class Type(ClassBasedTraitType):

    '''A trait whose value must be a subclass of a specified class.'''

    def __init__(self, default_value=None, klass=None, allow_none=True, **md):
        '''
        A Type trait specifies that its values must be subclasses of
        a particular class.

        If only ``default_value`` is given, it is used for the ``klass`` as
        well.

        Parameters
        ----------
        default_value : class, str or None
            The default value must be a subclass of klass.  If an str,
            the str must be a fully specified class name, like 'foo.bar.Bah'.
            The string is resolved into real class, when the parent
            :class:`HasTraits` class is instantiated.
        klass : class, str, None
            Values of this trait must be a subclass of klass.  The klass
            may be specified in a string like: 'foo.bar.MyClass'.
            The string is resolved into real class, when the parent
            :class:`HasTraits` class is instantiated.
        allow_none : boolean
            Indicates whether None is allowed as an assignable value. Even if
            ``False``, the default value may be ``None``.
        '''
        if default_value is None:
            if klass is None:
                klass = object
        elif klass is None:
            klass = default_value
        if not (inspect.isclass(klass) or isinstance(klass, basestring)):
            raise TraitError('A Type trait must specify a class.')
        self.klass = klass
        self._allow_none = allow_none
        super(Type, self).__init__(default_value, **md)

    def _resolve_classes(self):
        if isinstance(self.klass, basestring):
            self.klass = lazy_import(self.klass)
        if isinstance(self.default_value, basestring):
            self.default_value = lazy_import(self.default_value)

    def get_default_value(self):
        return self.default_value

    def info(self):
        '''Returns a description of the trait.'''
        if isinstance(self.klass, basestring):
            klass = self.klass
        else:
            klass = self.klass.__name__
        result = 'a subclass of ' + klass
        if self._allow_none:
            return result + ' or None'
        return result

    def instance_init(self, this):
        self._resolve_classes()
        super(Type, self).instance_init(this)

    def validate(self, this, value):
        '''Validates that the value is a valid object instance.'''
        try:
            if issubclass(value, self.klass):
                return value
        except:
            if (value is None) and (self._allow_none):
                return value
        self.error(this, value)


class DefaultValueGenerator(object):

    '''A class for generating new default value instances.'''

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def generate(self, klass):
        return klass(*self.args, **self.kw)


class Instance(ClassBasedTraitType):

    '''
    A trait whose value must be an instance of a specified class.

    The value can also be an instance of a subclass of the specified class.
    '''

    def __init__(self, klass=None, args=None, kw=None, allow_none=True, **md):
        '''
        Construct an Instance trait.

        This trait allows values that are instances of a particular class or
        its subclasses.  Our implementation is quite different from that of
        enthough.traits as we don't allow instances to be used for klass and we
        handle the ``args`` and ``kw`` arguments differently.

        Parameters
        ----------
        klass : class, str
            The class that forms the basis for the trait.  Class names
            can also be specified as strings, like 'foo.bar.Bar'.
        args : tuple
            Positional arguments for generating the default value.
        kw : dict
            Keyword arguments for generating the default value.
        allow_none : bool
            Indicates whether None is allowed as a value.

        Default Value
        -------------
        If both ``args`` and ``kw`` are None, then the default value is None.
        If ``args`` is a tuple and ``kw`` is a dict, then the default is
        created as ``klass(*args, **kw)``.  If either ``args`` or ``kw`` is not
        (but not both), None is replace by ``()`` or ``{}``.
        '''
        self._allow_none = allow_none
        if any([
            (klass is None),
            (not (inspect.isclass(klass) or isinstance(klass, basestring))),
        ]):
            raise TraitError(
                'klass argument must be a class you gave: %r' % klass
            )
        self.klass = klass
        # self.klass is a class, so handle default_value
        if args is None and kw is None:
            default_value = None
        else:
            if args is None:
                # kw is not None
                args = ()
            elif kw is None:
                # args is not None
                kw = {}
            if not isinstance(kw, dict):
                raise TraitError("'kw' argument must be a dict or None")
            if not isinstance(args, tuple):
                raise TraitError("'args' argument must be a tuple or None")
            default_value = DefaultValueGenerator(*args, **kw)
        super(Instance, self).__init__(default_value, **md)

    def _resolve_classes(self):
        if isinstance(self.klass, basestring):
            self.klass = lazy_import(self.klass)

    def get_default_value(self):
        '''
        Instantiate a default value instance.

        This is called when the containing HasTraits classes'
        :meth:`__new__` method is called to ensure that a unique instance
        is created for each HasTraits instance.
        '''
        dv = self.default_value
        if isinstance(dv, DefaultValueGenerator):
            return dv.generate(self.klass)
        return dv

    def info(self):
        if isinstance(self.klass, basestring):
            klass = self.klass
        else:
            klass = self.klass.__name__
        result = class_of(klass)
        if self._allow_none:
            return result + ' or None'
        return result

    def instance_init(self, this):
        self._resolve_classes()
        super(Instance, self).instance_init(this)

    def validate(self, this, value):
        if value is None:
            if self._allow_none:
                return value
            self.error(this, value)
        if isinstance(value, self.klass):
            return value
        else:
            self.error(this, value)


class This(ClassBasedTraitType):

    '''
    A trait for instances of the class containing this trait.

    Because how how and when class bodies are executed, the ``This`` trait can
    only have a default value of None.  This, and because we always validate
    default values, ``allow_none`` is *always* true.
    '''

    info_text = 'an instance of the same type as the receiver or None'

    def __init__(self, **md):
        super(This, self).__init__(None, **md)

    def validate(self, this, value):
        # What if value is a superclass of this.__class__?  This is
        # complicated if it was the superclass that defined the This
        # trait.
        if isinstance(value, self.this_class) or (value is None):
            return value
        else:
            self.error(this, value)


class ObjectName(TraitType):

    '''
    string holding a valid object name for this version of Python.

    This does not check that the name exists in any scope.
    '''

    info_text = 'a valid object identifier in Python'

    if sys.version_info[0] < 3:
        # Python 2:
        _name_re = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*$')

        def isidentifier(self, s):
            return bool(self._name_re.match(s))

        def coerce_str(self, this, value):
            'In Python 2, coerce ascii-only unicode to str'
            if isinstance(value, unicode):
                try:
                    return str(value)
                except UnicodeEncodeError:
                    self.error(this, value)
            return value
    else:
        # Python 3:
        isidentifier = staticmethod(lambda s: s.isidentifier())
        coerce_str = staticmethod(lambda _, s: s)

    def validate(self, this, value):
        value = self.coerce_str(this, value)
        if isinstance(value, str) and self.isidentifier(value):
            return value
        self.error(this, value)


class DottedObjectName(ObjectName):

    '''string holding a valid dotted object name in Python, such as A.b3._c'''

    def validate(self, this, value):
        value = self.coerce_str(this, value)
        if isinstance(value, str) and all(
            self.isidentifier(x) for x in value.split('.')
        ):
            return value
        self.error(this, value)