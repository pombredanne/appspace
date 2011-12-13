# encoding: utf-8
# pylint: disable-msg=w0212,w0702
'''
A lightweight Traits like module.

This is designed to provide a lightweight, simple, pure Python version of
many of the capabilities of enthought.traits.  This includes:

* Validation
* Type specification with defaults
* Static and dynamic notification
* Basic predefined types
* An API that is similar to enthought.traits

We don't support:

* Delegation
* Automatic GUI generation
* A full set of trait types.  Most importantly, we don't provide container
  traits (list, dict, tuple) that can trigger notifications if their
  contents change.
* API compatibility with enthought.traits

There are also some important difference in our design:

* enthought.traits does not validate default values.  We do.

We choose to create this module because we need these capabilities, but we need 
them to be pure Python so they work in all Python implementations, including 
Jython and IronPython.

Authors:

* Brian Granger
* Enthought, Inc. Some of the code in this file comes from enthought.traits
  and is licensed under the BSD license.  Also, many of the ideas also come
  from enthought.traits even though our implementation is very different.

Distributed under the terms of the BSD License. The full license is in
the file COPYING, distributed as part of this software.
'''

from __future__ import absolute_import
import re
import sys
import types
import inspect
from types import InstanceType, ClassType, FunctionType, ListType, TupleType

from .util import ResetMixin, class_name, deferred_import

ClassTypes = (ClassType, type)
SequenceTypes = (ListType, TupleType, set, frozenset)

## Utilities

def add_article(name):
    ''' 
    Returns a string containing the correct indefinite article ('a' or 'an')
    prefixed to the specified string.
    '''
    if name[:1].lower() in 'aeiou':
        return 'an ' + name
    return 'a ' + name

def class_of(this):
    ''' 
    Returns a string containing the class name of an object with the correct 
    indefinite article ('a' or 'an') preceding it.
    '''
    if isinstance(this, basestring):
        return add_article(this)
    return add_article(class_name(this))

def get_members(this, predicate=None):
    '''
    A safe version of inspect.getmembers that handles missing attributes.

    This is useful when there are descriptor based attributes that for some 
    reason raise AttributeError even though they exist.  This happens in 
    zope.inteface with the __provides__ attribute.
    '''
    results = []
    for key in dir(this):
        try:
            value = getattr(this, key)
        except AttributeError:
            pass
        else:
            if not predicate or predicate(value):
                results.append((key, value))
    results.sort()
    return results

def on_trait_change(name, post_init=False, *names):
    ''' 
    Marks the following method definition as being a handler for the extended 
    trait change specified by *name(s)*.

    Refer to the documentation for the on_trait_change() method of the 
    **HasTraits** class for information on the correct syntax for the *name(s)* 
    argument.

    A handler defined using this decorator is normally effective immediately. 
    However, if *post_init* is **True**, then the handler only become effective 
    after all object constructor arguments have been processed. That is, trait 
    values assigned as part of object construction will not cause the handler to 
    be invoked.
    '''
    def decorator (function):
        prefix = '<'
        if post_init:
            prefix = '>'
        function.on_trait_change = prefix + (','.join([name] + list(names)))
        return function
    return decorator

def parse_notifier_name(name):
    '''
    Convert the name argument to a list of names.
    
    Examples
    --------
    
    >>> parse_notifier_name('a')
    ['a']
    >>> parse_notifier_name(['a','b'])
    ['a', 'b']
    >>> parse_notifier_name(None)
    ['anytrait']
    '''
    if isinstance(name, str):
        return [name]
    elif name is None:
        return ['anytrait']
    elif isinstance(name, (list, tuple)):
        for n in name:
            assert isinstance(n, str), 'names must be strings'
        return name

def repr_type(this):
    '''
    Return a string representation of a value and its type for readable error 
    messages.
    '''
    the_type = type(this)
    if the_type is InstanceType:
        # Old-style class.
        the_type = this.__class__
    msg = '%r %r' % (this, the_type)
    return msg


## Basic classes


class NoDefaultSpecified(object):

    def generate(self, klass):
        pass


class TraitError(Exception):
    pass


class Undefined(object):
    pass


Undefined = Undefined()
NoDefaultSpecified = NoDefaultSpecified()


class _SimpleTest:

    def __init__ (self, value):
        self.value = value

    def __call__ (self, test):
        return test == self.value

    def __repr__(self):
        return '<SimpleTest(%r)' % self.value

    def __str__(self):
        return self.__repr__()


## Base TraitType for all traits


class TraitType(object):

    '''
    A base class for all trait descriptors.

    Notes
    -----
    Our implementation of traits is based on Python's descriptor prototol.  This 
    class is the base class for all such descriptors. The only magic we use is a 
    custom metaclass for the main :class:`HasTraits` class that does the 
    following:

    1. Sets the :attr:`name` attribute of every :class:`TraitType`
       instance in the class dict to the name of the attribute.
    2. Sets the :attr:`this_class` attribute of every :class:`TraitType`
       instance in the class dict to the *class* that declared the trait.
       This is used by the :class:`This` trait to allow subclasses to
       accept superclasses for :class:`This` values.
    '''

    default_value = Undefined
    info_text = 'any value'
    metadata = {}
    name = ''
    this_class = ''

    def __init__(self, default_value=NoDefaultSpecified, **md):
        if default_value is not NoDefaultSpecified:
            self.default_value = default_value
        if len(md) > 0:
            if len(self.metadata) > 0:
                self._metadata = self.metadata.copy()
                self._metadata.update(md)
            else:
                self._metadata = md
        else:
            self._metadata = self.metadata
        self.init()

    def __get__(self, this, cls=None):
        '''
        Get the value of the trait by self.name for the instance.

        Default values are instantiated when :meth:`HasTraits.__new__`
        is called.  Thus by the time this method gets called either the 
        default value or a user defined value (they called :meth:`__set__`)
        is in the :class:`HasTraits` instance.
        '''
        if this is None:
            return self
        else:
            try:
                value = this._trait_values[self.name]
            except KeyError:
                # Check for a dynamic initializer.
                if self.name in this._trait_dyn_inits:
                    value = this._trait_dyn_inits[self.name](this)
                    value = self._validate(this, value)
                    this._trait_values[self.name] = value
                    return value
                else:
                    raise TraitError(
                        'Unexpected error in TraitType: both default value and '
                        'dynamic initializer are absent'
                    )
            except Exception:
                # HasTraits should call set_default_value to populate
                # this.  So this should never be reached.
                raise TraitError(
                    'Unexpected error in TraitType: default value not set '
                    'properly'
                )
            else:
                return value

    def __set__(self, this, value):
        new_value = self._validate(this, value)
        old_value = self.__get__(this)
        if old_value != new_value:
            this._trait_values[self.name] = new_value
            this._notify_trait(self.name, old_value, new_value)

    def _validate(self, this, value):
        if hasattr(self, 'validate'):
            return self.validate(this, value)
        elif hasattr(self, 'is_valid_for'):
            valid = self.is_valid_for(value)
            if valid:
                return value
            raise TraitError('invalid value for type: %r' % value)
        elif hasattr(self, 'value_for'):
            return self.value_for(value)
        return value

    def get_default_value(self):
        '''Create a new instance of the default value.'''
        return self.default_value

    def init(self):
        pass

    def info(self):
        return self.info_text

    def instance_init(self, this):
        '''
        This is called by :meth:`HasTraits.__new__` to finish init'ing.

        Some stages of initialization must be delayed until the parent
        :class:`HasTraits` instance has been created.  This method is called in 
        :meth:`HasTraits.__new__` after the instance has been created.

        This method trigger the creation and validation of default values and 
        also things like the resolution of str given class names in 
        :class:`Type` and :class`Instance`.

        Parameters
        ----------
        this : :class:`HasTraits` instance
            The parent :class:`HasTraits` instance that has just been created.
        '''
        self.set_default_value(this)

    def is_valid_for(self, value):
        pass

    def error(self, this, value):
        if this is not None:
            e = '%s trait of %s instance must be %s, but value %s specified' % (
                self.name, class_of(this), self.info(), repr_type(value)
            )
        else:
            e = '%s trait must be %s, but a value of %r was specified' % (
                self.name, self.info(), repr_type(value)
            )
        raise TraitError(e)

    def get_metadata(self, key):
        return getattr(self, '_metadata', {}).get(key, None)

    def set_default_value(self, this):
        '''
        Set the default value on a per instance basis.

        This method is called by :meth:`instance_init` to create and validate 
        the default value.  The creation and validation of default values must 
        be delayed until the parent :class:`HasTraits` class has been 
        instantiated.
        '''
        # Check for a deferred initializer defined in the same class as the
        # trait declaration or above.
        mro = type(this).mro()
        cls = None
        meth_name = '_%s_default' % self.name
        for cls in mro[:mro.index(self.this_class) + 1]:
            if meth_name in cls.__dict__:
                break
        else:
            # We didn't find one. Do static initialization.
            dv = self.get_default_value()
            newdv = self._validate(this, dv)
            this._trait_values[self.name] = newdv
            return
        # Complete the dynamic initialization.
        this._trait_dyn_inits[self.name] = cls.__dict__[meth_name]

    def set_metadata(self, key, value):
        getattr(self, '_metadata', {})[key] = value

    def validate(self, this, value):
        pass

    def value_for(self, this, value):
        pass


## The HasTraits implementation


class MetaHasTraits(type):

    '''
    A metaclass for HasTraits.
    
    This metaclass makes sure that any TraitType class attributes are
    instantiated and sets their name attribute.
    '''

    def __new__(cls, name, bases, classdict):
        '''
        This instantiates all TraitTypes in the class dict and sets their
        :attr:`name` attribute.
        '''
        for k, v in classdict.iteritems():
            if isinstance(v, TraitType):
                v.name = k
            elif inspect.isclass(v):
                if issubclass(v, TraitType):
                    vinst = v()
                    vinst.name = k
                    classdict[k] = vinst
        return super(MetaHasTraits, cls).__new__(cls, name, bases, classdict)

    def __init__(cls, name, bases, classdict):
        '''
        Finish initializing HasTraits class.
        
        This sets the :attr:`this_class` attribute of each TraitType in the
        class dict to the newly created class ``cls``.
        '''
        for v in classdict.itervalues():
            if isinstance(v, TraitType):
                v.this_class = cls
        super(MetaHasTraits, cls).__init__(name, bases, classdict)


class HasTraits(ResetMixin):

    __metaclass__ = MetaHasTraits

    def __new__(cls, **kw):
        # This is needed because in Python 2.6 object.__new__ only accepts
        # the cls argument.
        new_meth = super(HasTraits, cls).__new__
        if new_meth is object.__new__:
            inst = new_meth(cls)
        else:
            inst = new_meth(cls, **kw)
        inst._trait_values = {}
        inst._trait_notifiers = {}
        inst._trait_dyn_inits = {}
        # Here we tell all the TraitType instances to set their default
        # values on the instance. 
        for key in dir(cls):
            # Some descriptors raise AttributeError like zope.interface's
            # __provides__ attributes even though they exist.  This causes
            # AttributeErrors even though they are listed in dir(cls).
            try:
                value = getattr(cls, key)
            except AttributeError:
                pass
            else:
                if isinstance(value, TraitType):
                    value.instance_init(inst)
        return inst

    def __init__(self, **kw):
        # Allow trait values to be set using keyword arguments. We need to use 
        # setattr for this to trigger validation and notifications.
        super(HasTraits, self).__init__()
        for key, value in kw.iteritems():
            setattr(self, key, value)

    def _add_notifiers(self, handler, name):
        if not self._trait_notifiers.has_key(name):
            nlist = []
            self._trait_notifiers[name] = nlist
        else:
            nlist = self._trait_notifiers[name]
        if handler not in nlist:
            nlist.append(handler)

    def _notify_trait(self, name, old_value, new_value):
        # First dynamic ones
        callables = self._trait_notifiers.get(name, [])
        more_callables = self._trait_notifiers.get('anytrait', [])
        callables.extend(more_callables)
        # Now static ones
        try:
            cb = getattr(self, '_%s_changed' % name)
        except:
            pass
        else:
            callables.append(cb)
        # Call them all now
        for c in callables:
            # Traits catches and logs errors here.  I allow them to raise
            if callable(c):
                argspec = inspect.getargspec(c)
                nargs = len(argspec[0])
                # Bound methods have an additional 'self' argument
                # I don't know how to treat unbound methods, but they
                # can't really be used for callbacks.
                if isinstance(c, types.MethodType):
                    offset = -1
                else:
                    offset = 0
                if nargs + offset == 0:
                    c()
                elif nargs + offset == 1:
                    c(name)
                elif nargs + offset == 2:
                    c(name, new_value)
                elif nargs + offset == 3:
                    c(name, old_value, new_value)
                else:
                    raise TraitError(
                        'trait changed callback must have 0-3 arguments'
                    )
            else:
                raise TraitError('trait changed callback must be callable')

    def _remove_notifiers(self, handler, name):
        if self._trait_notifiers.has_key(name):
            nlist = self._trait_notifiers[name]
            try:
                index = nlist.index(handler)
            except ValueError:
                pass
            else:
                del nlist[index]

    @classmethod
    def class_trait_names(cls, **md):
        '''
        Get a list of all the names of this classes traits.

        This method is just like the :meth:`trait_names` method, but is unbound.
        '''
        return cls.class_traits(**md).keys()

    @classmethod
    def class_traits(cls, **md):
        '''
        Get a list of all the traits of this class.

        This method is just like the :meth:`traits` method, but is unbound.

        The TraitTypes returned don't know anything about the values that the 
        various HasTrait's instances are holding.

        This follows the same algorithm as traits does and does not allow for 
        any simple way of specifying merely that a metadata name exists, but has 
        any value.  This is because get_metadata returns None if a metadata key 
        doesn't exist.
        '''
        traits = dict(
            m for m in get_members(cls) if isinstance(m[1], TraitType)
        )
        if len(md) == 0:
            return traits
        for meta_name, meta_eval in md.items():
            if type(meta_eval) is not FunctionType:
                md[meta_name] = _SimpleTest(meta_eval)
        result = {}
        for name, trait in traits.items():
            for meta_name, meta_eval in md.items():
                if not meta_eval(trait.get_metadata(meta_name)):
                    break
            else:
                result[name] = trait
        return result

    def on_trait_change(self, handler, name=None, remove=False):
        '''
        Setup a handler to be called when a trait changes.

        This is used to setup dynamic notifications of trait changes.
        
        Static handlers can be created by creating methods on a HasTraits
        subclass with the naming convention '_[traitname]_changed'.  Thus,
        to create static handler for the trait 'a', create the method
        _a_changed(self, name, old, new) (fewer arguments can be used, see
        below).
        
        Parameters
        ----------
        handler : callable
            A callable that is called when a trait changes.  Its 
            signature can be handler(), handler(name), handler(name, new)
            or handler(name, old, new).
        name : list, str, None
            If None, the handler will apply to all traits.  If a list of str, 
            handler will apply to all names in the list.  If a str, the handler 
            will apply just to that name.
        remove : bool
            If False (the default), then install the handler.  If True then 
            uninstall it.
        '''
        if remove:
            names = parse_notifier_name(name)
            for n in names:
                self._remove_notifiers(handler, n)
        else:
            names = parse_notifier_name(name)
            for n in names:
                self._add_notifiers(handler, n)

    def trait_metadata(self, traitname, key):
        '''Get metadata values for trait by key.'''
        try:
            trait = getattr(self.__class__, traitname)
        except AttributeError:
            raise TraitError('Class %s does not have a trait named %s' % (
                class_name(self), traitname
            ))
        else:
            return trait.get_metadata(key)

    def trait_names(self, **md):
        '''Get a list of all the names of this classes traits.'''
        return self.traits(**md).keys()

    def trait_set(self, trait_change_notify=True, **traits):
        '''
        Shortcut for setting object trait attributes.

        Parameters
        ----------
        trait_change_notify : Boolean
            If **True** (the default), then each value assigned may generate a
            trait change notification. If **False**, then no trait change
            notifications will be generated. (see also: trait_setq)
        traits : list of key/value pairs
            Trait attributes and their values to be set

        Returns
        -------
        self
            The method returns this object, after setting attributes.

        Description
        -----------
        Treats each keyword argument to the method as the name of a trait
        attribute and sets the corresponding trait attribute to the value
        specified. This is a useful shorthand when a number of trait attributes
        need to be set on an object, or a trait attribute value needs to be set
        in a lambda function. For example, you can write::

            person.trait_set(name='Bill', age=27)

        instead of::

            person.name = 'Bill'
            person.age = 27
        '''
        if not trait_change_notify:
            self._notify_trait(False)
            try:
                for name, value in traits.items():
                    setattr(self, name, value)
            finally:
                self._notify_trait(True)
        else:
            for name, value in traits.items():
                setattr(self, name, value)
        return self

    def traits(self, **md):
        '''
        Get a list of all the traits of this class.

        The TraitTypes returned don't know anything about the values that the 
        various HasTrait's instances are holding.

        This follows the same algorithm as traits does and does not allow for 
        any simple way of specifying merely that a metadata name exists, but 
        has any value.  This is because get_metadata returns None if a metadata 
        key doesn't exist.
        '''
        traits = dict(
            m for m in get_members(self.__class__) if isinstance(m[1], TraitType)
        )
        if len(md) == 0:
            return traits
        for meta_name, meta_eval in md.items():
            if type(meta_eval) is not FunctionType:
                md[meta_name] = _SimpleTest(meta_eval)
        result = {}
        for name, trait in traits.items():
            for meta_name, meta_eval in md.items():
                if not meta_eval(trait.get_metadata(meta_name)):
                    break
            else:
                result[name] = trait
        return result

    def trait_reset(self, traits=None, **metadata):
        ''' 
        Resets some or all of an object's trait attributes to their default
        values.

        Parameters
        ----------
        traits : list of strings
            Names of trait attributes to reset

        Returns
        -------
        A list of attributes that the method was unable to reset, which is empty
        if all the attributes were successfully reset.

        Description
        -----------
        Resets each of the traits whose names are specified in the *traits* list
        to their default values. If *traits* is None or omitted, the method
        resets all explicitly-defined object trait attributes to their default
        values. Note that this does not affect wildcard trait attributes or
        trait attributes added via add_trait(), unless they are explicitly
        named in *traits*.
        '''
        unresetable = []
        if traits is None:
            traits = self.trait_names(**metadata)
        for name in traits:
            try:
                delattr(self, name)
            except (AttributeError, TraitError):
                unresetable.append(name)
        return unresetable


## Actual TraitTypes implementations/subclasses

## TraitTypes subclasses for handling classes and instances of classes


class ClassBasedTraitType(TraitType):

    '''A trait with error reporting for Type, Instance and This.'''

    def error(self, this, value):
        kind = type(value)
        if kind is InstanceType:
            msg = 'class %s' % class_name(value)
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

    def __init__ (self, default_value=None, klass=None, allow_none=True, **md):
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
            self.klass = deferred_import(self.klass)
        if isinstance(self.default_value, basestring):
            self.default_value = deferred_import(self.default_value)

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

        This trait allows values that are instances of a particular class or its 
        subclasses.  Our implementation is quite different from that of 
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
        If ``args`` is a tuple and ``kw`` is a dict, then the default is created 
        as ``klass(*args, **kw)``.  If either ``args`` or ``kw`` is not (but not 
        both), None is replace by ``()`` or ``{}``.
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
            self.klass = deferred_import(self.klass)

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


# Basic TraitTypes implementations/subclasses


class Any(TraitType):

    default_value = None
    info_text = 'any value'


class Int(TraitType):

    '''A integer trait.'''

    default_value = 0
    info_text = 'an integer'

    def validate(self, this, value):
        if isinstance(value, int):
            return value
        self.error(this, value)


class CInt(Int):

    '''A casting version of the int trait.'''

    def validate(self, this, value):
        try:
            return int(value)
        except:
            self.error(this, value)


class Long(TraitType):

    '''A long integer trait.'''

    default_value = 0L
    info_text = 'a long'

    def validate(self, this, value):
        if isinstance(value, long):
            return value
        if isinstance(value, int):
            return long(value)
        self.error(this, value)


class CLong(Long):

    '''A casting version of the long integer trait.'''

    def validate(self, this, value):
        try:
            return long(value)
        except:
            self.error(this, value)


class Float(TraitType):

    '''A float trait.'''

    default_value = 0.0
    info_text = 'a float'

    def validate(self, this, value):
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        self.error(this, value)


class CFloat(Float):

    '''A casting version of the float trait.'''

    def validate(self, this, value):
        try:
            return float(value)
        except:
            self.error(this, value)


class Complex(TraitType):

    '''A trait for complex numbers.'''

    default_value = 0.0 + 0.0j
    info_text = 'a complex number'

    def validate(self, this, value):
        if isinstance(value, complex):
            return value
        if isinstance(value, (float, int)):
            return complex(value)
        self.error(this, value)


class CComplex(Complex):

    '''A casting version of the complex number trait.'''

    def validate (self, this, value):
        try:
            return complex(value)
        except:
            self.error(this, value)


# We should always be explicit about whether we're using bytes or unicode, both
# for Python 3 conversion and for reliable unicode behaviour on Python 2. So
# we don't have a Str type.
class Bytes(TraitType):

    '''A trait for strings.'''

    default_value = ''
    info_text = 'a string'

    def validate(self, this, value):
        if isinstance(value, bytes):
            return value
        self.error(this, value)


class CBytes(Bytes):

    '''A casting version of the string trait.'''

    def validate(self, this, value):
        try:
            return bytes(value)
        except:
            self.error(this, value)


class Unicode(TraitType):

    '''A trait for unicode strings.'''

    default_value = u''
    info_text = 'a unicode string'

    def validate(self, this, value):
        if isinstance(value, unicode):
            return value
        if isinstance(value, bytes):
            return unicode(value)
        self.error(this, value)


class CUnicode(Unicode):

    '''A casting version of the unicode trait.'''

    def validate(self, this, value):
        try:
            return unicode(value)
        except:
            self.error(this, value)


class ObjectName(TraitType):

    '''
    A string holding a valid object name in this version of Python.
    
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

    '''A string holding a valid dotted object name in Python, such as A.b3._c'''

    def validate(self, this, value):
        value = self.coerce_str(this, value)
        if isinstance(value, str) and all(
            self.isidentifier(x) for x in value.split('.')
        ):
            return value
        self.error(this, value)


class Bool(TraitType):

    '''A boolean (True, False) trait.'''

    default_value = False
    info_text = 'a boolean'

    def validate(self, this, value):
        if isinstance(value, bool):
            return value
        self.error(this, value)


class CBool(Bool):

    '''A casting version of the boolean trait.'''

    def validate(self, this, value):
        try:
            return bool(value)
        except:
            self.error(this, value)


class Enum(TraitType):

    '''An enum that whose value must be in a given sequence.'''

    def __init__(self, values, default_value=None, allow_none=True, **md):
        self.values = values
        self._allow_none = allow_none
        super(Enum, self).__init__(default_value, **md)

    def info(self):
        ''' Returns a description of the trait.'''
        result = 'any of ' + repr(self.values)
        if self._allow_none:
            return result + ' or None'
        return result

    def validate(self, this, value):
        if value is None:
            if self._allow_none:
                return value
        if value in self.values:
            return value
        self.error(this, value)


class CaselessStrEnum(Enum):

    '''An enum of strings that are caseless in validate.'''

    def validate(self, this, value):
        if value is None:
            if self._allow_none:
                return value
        if not isinstance(value, basestring):
            self.error(this, value)
        for v in self.values:
            if v.lower() == value.lower():
                return v
        self.error(this, value)


class Container(Instance):

    '''
    An instance of a container (list, set, etc.)

    To be subclassed by overriding klass.
    '''

    klass = None
    _valid_defaults = SequenceTypes
    _trait = None

    def __init__(self, trait=None, default_value=None, allow_none=True, **md):
        '''Create a container trait type from a list, set, or tuple.

        The default value is created by doing ``List(default_value)``, which 
        creates a copy of the ``default_value``.

        ``trait`` can be specified, which restricts the type of elements in the 
        container to that TraitType.

        If only one arg is given and it is not a Trait, it is taken as
        ``default_value``:

        ``c = List([1,2,3])``

        Parameters
        ----------

        trait : TraitType [ optional ]
            the type for restricting the contents of the Container. If 
            unspecified, types are not checked.

        default_value : SequenceType [ optional ]
            The default value for the Trait.  Must be list/tuple/set, and will 
            be cast to the container type.

        allow_none : Bool [ default True ]
            Whether to allow the value to be None

        **md : any
            further keys for extensions to the Trait (e.g. config)
        '''
        istrait = lambda t: isinstance(t, type) and issubclass(t, TraitType)
        # allow List([values]):
        if default_value is None and not istrait(trait):
            default_value = trait
            trait = None
        if default_value is None:
            args = ()
        elif isinstance(default_value, self._valid_defaults):
            args = (default_value,)
        else:
            raise TypeError('default value of %s was %s' % (
                class_name(self), default_value)
            )
        if istrait(trait):
            self._trait = trait()
            self._trait.name = 'element'
        elif trait is not None:
            raise TypeError(
                '`trait` must be a Trait or None, got %s' % repr_type(trait)
            )
        super(Container, self).__init__(
            klass=self.klass, args=args, allow_none=allow_none, **md
        )

    def element_error(self, this, element, validator):
        e = '%s trait element of %s instance must be %s but value %s specified' % (
            self.name, class_of(this), validator.info(), repr_type(element)
        )
        raise TraitError(e)

    def validate(self, this, value):
        value = super(Container, self).validate(this, value)
        if value is None:
            return value
        value = self.validate_elements(this, value)
        return value

    def validate_elements(self, this, value):
        validated = []
        if self._trait is None or isinstance(self._trait, Any):
            return value
        for v in value:
            try:
                v = self._trait.validate(this, v)
            except TraitError:
                self.element_error(this, v, self._trait)
            else:
                validated.append(v)
        return self.klass(validated)


class List(Container):

    '''An instance of a Python list.'''

    klass = list

    def __init__(
        self, trait=None, default_value=None, minlen=0, maxlen=sys.maxint,
        allow_none=True, **md
    ):
        '''Create a List trait type from a list, set, or tuple.

        The default value is created by doing ``List(default_value)``,
        which creates a copy of the ``default_value``.

        ``trait`` can be specified, which restricts the type of elements
        in the container to that TraitType.

        If only one arg is given and it is not a Trait, it is taken as
        ``default_value``:

        ``c = List([1,2,3])``

        Parameters
        ----------

        trait : TraitType [ optional ]
            the type for restricting the contents of the Container.  If 
            unspecified, types are not checked.

        default_value : SequenceType [ optional ]
            The default value for the Trait.  Must be list/tuple/set, and
            will be cast to the container type.

        minlen : Int [ default 0 ]
            The minimum length of the input list

        maxlen : Int [ default sys.maxint ]
            The maximum length of the input list

        allow_none : Bool [ default True ]
            Whether to allow the value to be None

        **md : any
            further keys for extensions to the Trait (e.g. config)
        '''
        self._minlen = minlen
        self._maxlen = maxlen
        super(List, self).__init__(
            trait=trait, default_value=default_value, allow_none=allow_none,
            **md
        )

    def length_error(self, this, value):
        e = '%s trait of %s instance must be length %i <= L <= %i but value %s specified' % (
            self.name, class_of(this), self._minlen, self._maxlen, value,
        )
        raise TraitError(e)

    def validate_elements(self, this, value):
        length = len(value)
        if length < self._minlen or length > self._maxlen:
            self.length_error(this, value)
        return super(List, self).validate_elements(this, value)


class Set(Container):

    '''An instance of a Python set.'''

    klass = set


class Tuple(Container):

    '''An instance of a Python tuple.'''

    klass = tuple

    def __init__(self, *traits, **md):
        '''
        Tuple(*traits, default_value=None, allow_none=True, **medatata)

        Create a tuple from a list, set, or tuple.

        Create a fixed-type tuple with Traits:

        ``t = Tuple(Int, Str, CStr)``

        would be length 3, with Int,Str,CStr for each element.

        If only one arg is given and it is not a Trait, it is taken as
        default_value:

        ``t = Tuple((1,2,3))``

        Otherwise, ``default_value`` *must* be specified by keyword.

        Parameters
        ----------

        *traits : TraitTypes [ optional ]
            the tsype for restricting the contents of the Tuple. If unspecified,
            types are not checked. If specified, then each positional argument
            corresponds to an element of the tuple. Tuples defined with traits
            are of fixed length.

        default_value : SequenceType [ optional ]
            The default value for the Tuple.  Must be list/tuple/set, and
            will be cast to a tuple. If `traits` are specified, the
            `default_value` must conform to the shape and type they specify.

        allow_none : Bool [ default True ]
            Whether to allow the value to be None

        **md : any
            further keys for extensions to the Trait (e.g. config)
        '''
        default_value = md.pop('default_value', None)
        allow_none = md.pop('allow_none', True)
        istrait = lambda t: isinstance(t, type) and issubclass(t, TraitType)
        # allow Tuple((values,)):
        if all([
            len(traits) == 1,
            default_value is None,
            not istrait(traits[0]),
        ]):
            default_value = traits[0]
            traits = ()
        if default_value is None:
            args = ()
        elif isinstance(default_value, self._valid_defaults):
            args = (default_value,)
        else:
            raise TypeError('default value of %s was %s' % (
                class_name(self), default_value
            ))
        self._traits = []
        for trait in traits:
            t = trait()
            t.name = 'element'
            self._traits.append(t)
        if self._traits and default_value is None:
            # don't allow default to be an empty container if length specified
            args = None
        super(Tuple, self).__init__(
            klass=self.klass, args=args, allow_none=allow_none, **md
        )

    def validate_elements(self, this, value):
        if not self._traits:
            # nothing to validate
            return value
        if len(value) != len(self._traits):
            e = '%s trait of %s instance requires %i elements but value %s specified' % (
                self.name, class_of(this), len(self._traits), repr_type(value)
            )
            raise TraitError(e)
        validated = []
        for t, v in zip(self._traits, value):
            try:
                v = t.validate(this, v)
            except TraitError:
                self.element_error(this, v, t)
            else:
                validated.append(v)
        return tuple(validated)


class Dict(Instance):

    '''An instance of a Python dict.'''

    def __init__(self, default_value=None, allow_none=True, **md):
        '''
        Create a dict trait type from a dict.

        The default value is created by doing ``dict(default_value)``, which 
        creates a copy of the ``default_value``.
        '''
        if default_value is None:
            args = ((),)
        elif isinstance(default_value, dict):
            args = (default_value,)
        elif isinstance(default_value, SequenceTypes):
            args = (default_value,)
        else:
            raise TypeError('default value of Dict was %s' % default_value)
        super(Dict, self).__init__(
            klass=dict, args=args, allow_none=allow_none, **md
        )


class TCPAddress(TraitType):

    '''
    A trait for an (ip, port) tuple.

    This allows for both IPv4 IP addresses as well as hostnames.
    '''

    default_value = ('127.0.0.1', 0)
    info_text = 'an (ip, port) tuple'

    def validate(self, this, value):
        if isinstance(value, tuple):
            if len(value) == 2:
                if all([
                    isinstance(value[0], basestring), isinstance(value[1], int)
                ]):
                    port = value[1]
                    if port >= 0 and port <= 65535:
                        return value
        self.error(this, value)
