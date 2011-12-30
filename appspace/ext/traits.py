# -*- coding: utf-8 -*-
'''appspace traits'''

from __future__ import absolute_import

from types import FunctionType

from stuf.utils import clsname, either, getter, deleter, setter

from appspace.error import TraitError
from appspace.decorators import TraitType
from appspace.utils import get_members, getcls


class _SimpleTest:

    def __init__(self, value):
        self.value = value

    def __call__(self, test):
        return test == self.value

    def __repr__(self):
        return '<SimpleTest(%r)' % self.value

    def __str__(self):
        return self.__repr__()


class Traits(object):

    def __init__(self, this):
        self.this = this

    @staticmethod
    def _filter(traits, **md):
        '''
        get a list of all the traits of this class.

        This method a class method equivalent of the `traits` method.

        The traits returned know nothing about the values that HasTrait's
        instances are holding.

        This follows the same algorithm as traits does and does not allow for
        any simple way of specifying merely that a metadata name exists, but
        has any value.  This is because get_metadata returns None if a metadata
        key doesn't exist.
        '''
        if not md:
            return traits
        for meta_name, meta_eval in md.itemitems():
            if type(meta_eval) is not FunctionType:
                md[meta_name] = _SimpleTest(meta_eval)
        result = {}
        for name, trait in traits.iteritems():
            get_metadata = trait.get_metadata
            for meta_name, meta_eval in md.itemitems():
                if not meta_eval(get_metadata(meta_name)):
                    break
            else:
                result[name] = trait
        return result

    @either
    def _traits(self):
        return dict(
            m for m in get_members(getcls(self)) if TraitType.instance(m[1])
        )

    @classmethod
    def class_filter(cls, **md):
        '''
        get a list of all the traits of this class.

        This method a class method equivalent of the `traits` method.

        The traits returned know nothing about the values that HasTrait's
        instances are holding.

        This follows the same algorithm as traits does and does not allow for
        any simple way of specifying merely that a metadata name exists, but
        has any value.  This is because get_metadata returns None if a metadata
        key doesn't exist.
        '''
        return cls._filter(cls._traits, **md)

    @classmethod
    def class_names(cls, **md):
        '''
        Get a list of all the names of this classes traits.

        This method is just like the :meth:`trait_names` method, but is unbound
        '''
        return cls.class_filter(**md).keys()

    def commit(self):
        self._sync.commit()
        self.sync()

    def find(self, **md):
        '''
        get trait list for class

        Returned TraitTypes know nothing about other values that any other of
        HasTrait's instances are holding.

        This follows the same algorithm as traits does and does not allow for
        any simple way of specifying merely that a metadata name exists, but
        has any value.  This is because get_metadata returns None if a metadata
        key doesn't exist.
        '''
        return self._filter(self._traits, **md)

    def metadata(self, label, key):
        '''
        get metadata values for trait by key

        @param label: trait label
        @param key: key in trait metadata
        '''
        try:
            return getter(getcls(self.this), label).get_metadata(key)
        except AttributeError:
            raise TraitError(
                '%s has no trait %s' % (clsname(self.this), label)
            )

    def names(self, **md):
        '''get all names of this instance's traits.'''
        return self.find(**md).keys()

    def reset(self, labels=None, **metadata):
        '''
        Resets each of the traits whose names are specified in the *traits*
        list to their default values. If *traits* is None or omitted, the
        method resets all explicitly-defined object trait attributes to their
        default values. A list of attributes that the method was unable to
        reset, which is empty if all the attributes were successfully reset.

        @param traits: list of strings naming trait attributes to reset
        '''
        unresetable = []
        uappend = unresetable.append
        if labels is None:
            labels = self.names(**metadata)
        this = self.this
        for label in labels:
            try:
                deleter(this, label)
            except (AttributeError, TraitError):
                uappend(label)
        return unresetable

    def set(self, notify=True, **traits):
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
        this = self.this
        if not notify:
            this.a.events.enabled = False
            try:
                for name, value in traits.iteritems():
                    setter(this, name, value)
            finally:
                this.a.events.enabled = True
            return self
        for name, value in traits.items():
            setter(this, name, value)
        return self

    def sync(self, **kw):
        '''synchronize traits with current instance property values'''
        cur = self._sync.current
        self.set(**dict((k, cur[k]) for k in self.names(**kw)))

    def update(self, **kw):
        sync = self.this._sync
        if sync.changed:
            sync.current.update(sync.changed.copy())
        else:
            self.sync(**kw)

    def validate_one(self, trait, value):
        try:
            if self._traits[trait].validate(trait, value):
                return True
        except KeyError:
            return False

    def validate_many(self):
        '''validate model data'''
        for k, v in self._sync.current.iteritems():
            if not self.validate_one(k, v):
                return False
        return True
