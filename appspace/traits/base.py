# -*- coding: utf-8 -*-
# pylint: disable-msg=w0702,w0232
'''base Trait classes'''

from __future__ import absolute_import

import types
import inspect
from types import FunctionType

from stuf.utils import clsname, either

from appspace.utils import get_members, parse_notifier_name

from .error import TraitError
from .support import Sync, _SimpleTest
from .trait_types.base import TraitType


class SynchedMixin(object):

    def __init__(self, original, **kw):
        # Allow trait values to be set using keyword arguments. We need to use
        # setattr for this to trigger validation and notifications.
        super(SynchedMixin, self).__init__()
        self._sync = Sync(original, **kw)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))

    __str__ = __unicode__


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


class HasTraitsMixin(SynchedMixin):

    __metaclass__ = MetaHasTraits
    _descriptor_class = TraitType
    c = None

    def __new__(cls, *args, **kw):
        # This is needed because in Python 2.6 object.__new__ only accepts
        # the cls argument.
        # pylint: disable-msg=e1101
        cls._metas = [
            b.Meta for b in inspect.getmro(cls) if hasattr(b, 'Meta')
        ]
        # pylint: enable-msg=e1101
        new_meth = super(HasTraitsMixin, cls).__new__
        if new_meth is object.__new__:
            inst = new_meth(cls)
        else:
            inst = new_meth(cls, *args, **kw)
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

    def _add_notifiers(self, handler, name):
        if not name in self._trait_notifiers:
            nlist = []
            self._trait_notifiers[name] = nlist
        else:
            nlist = self._trait_notifiers[name]
        if handler not in nlist:
            nlist.append(handler)

    def _remove_notifiers(self, handler, name):
        if name in self._trait_notifiers:
            nlist = self._trait_notifiers[name]
            try:
                index = nlist.index(handler)
            except ValueError:
                pass
            else:
                del nlist[index]

    def _trait_notify(self, name, old_value, new_value):
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

    @either
    def _traits(self):
        return dict(
            m for m in get_members(self.__class__)
            if isinstance(m[1], TraitType)
        )

    @classmethod
    def class_trait_names(cls, **md):
        '''
        Get a list of all the names of this classes traits.

        This method is just like the :meth:`trait_names` method, but is unbound
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
        any simple way of specifying merely that a metadata name exists, but
        has any value.  This is because get_metadata returns None if a metadata
        key doesn't exist.
        '''
        traits = cls._traits
        if not md:
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
                clsname(self), traitname
            ))
        else:
            return trait.get_metadata(key)

    def trait_names(self, **md):
        '''Get a list of all the names of this classes traits.'''
        return self.traits(**md).keys()

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
        A list of attributes that the method was unable to reset, which is
        empty if all the attributes were successfully reset.

        Description
        -----------
        Resets each of the traits whose names are specified in the *traits*
        list to their default values. If *traits* is None or omitted, the
        method resets all explicitly-defined object trait attributes to their
        default values.
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

    def trait_set(self, trait_change_notify=True, **traits):
        '''
        Shortcut for setting object trait attributes.

        Parameters
        ----------
        trait_change_notify : Boolean
            If **True** (the default), then each value assigned may generate a
            trait change notification. If **False**, then no trait change
            notifications will be generated. (see also: trait_setq)
        traits: list of key/value pairs
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
            self._trait_notify(False)
            try:
                for name, value in traits.items():
                    setattr(self, name, value)
            finally:
                self._trait_notify(True)
        else:
            for name, value in traits.items():
                setattr(self, name, value)
        return self

    def trait_validate(self, trait, value):
        try:
            trait_class = self._traits[trait]
            if trait_class.validate(trait, value):
                return True
        except KeyError:
            return False

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
        traits = self._traits
        if not md:
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

    def traits_sync(self, **kw):
        '''synchronize traits with current instance property values'''
        cur = self._sync.current
        self.trait_set(**{k: cur[k] for k in self.trait_names(**kw)})

    def traits_update(self, **kw):
        if self._sync.changed:
            self._sync.current.update(self._sync.changed.copy())
        else:
            self.traits_sync(**kw)

    def traits_validate(self):
        '''validate model data'''
        for k, v in self._sync.current.iteritems():
            if not self.trait_validate(k, v):
                return False
        return True

    def traits_commit(self):
        self._sync.commit()
        self.traits_sync()

    class Meta:
        pass
