# -*- coding: utf-8 -*-
'''appspace traits classes'''

from __future__ import absolute_import

from inspect import isclass
from types import FunctionType

from stuf.utils import both, clsname, getcls, getter, deleter, setter

from appspace.ext import Synced
from appspace.keys import appifies

from .query import T
from .keys import ATraits
from .core import TraitType
from .error import TraitError


class MetaTraits(type):

    '''
    metaclass to make sure TraitType class attributes are instantiated with
    their name attribute set.
    '''

    def __new__(cls, name, bases, classdict):
        '''
        new

        instantiate TraitTypes in classdict, setting their name attribute
        '''
        istrait = T.istrait
        for k, v in classdict.iteritems():
            if istrait(k, v):
                if isclass(v):
                    vinst = v()
                    vinst.name = k
                    classdict[k] = vinst
                else:
                    v.name = k
        return super(MetaTraits, cls).__new__(cls, name, bases, classdict)

    def __init__(cls, name, bases, classdict):
        '''
        init

        finish initializing Traits class

        This sets this_class attribute of each TraitType in the classdict to a
        newly created class.
        '''
        istrait = T.istrait
        cls._classtraits = classtraits = {}
        for k, v in classdict.iteritems():
            if istrait(k, v):
                v.this_class = cls
                classtraits[k] = v
        super(MetaTraits, cls).__init__(name, bases, classdict)


class Traits(Synced):

    __metaclass__ = MetaTraits

    appifies(ATraits)

    _descriptor = TraitType

    def __new__(cls, *args, **kw):
        '''
        new

        initalize traits for instance
        '''
        inst = super(Traits, cls).__new__(cls, *args, **kw)
        traits = inst._traits = {}
        istrait = T.istrait
        # set all TraitType instances to their default values
        for k, v in vars(cls).iteritems():
            if istrait(k, v):
                v.instance_init(inst)
                traits[k] = v
        return inst

    @both
    def C(self):
        '''local settings'''
        return T(self).localize().one()

    @staticmethod
    def _filter(traits, **metadata):
        '''
        get a list of all the traits of this class

        @param traits: traits
        @param **metadata: metadata to filter by

        This method is a class method equivalent of the traits method.

        The traits returned know nothing about the values that Traits'
        instances are holding.

        This follows the same algorithm as traits does and does not allow for
        any simple way of specifying merely that a metadata name exists, but
        has any value.  This is because get_metadata returns None if a metadata
        key doesn't exist.
        '''
        if not metadata:
            return traits
        for meta_name, meta_eval in metadata.iteritems():
            if type(meta_eval) is not FunctionType:
                metadata[meta_name] = _SimpleTest(meta_eval)
        result = {}
        for name, trait in traits.iteritems():
            get_metadata = trait.get_metadata
            for meta_name, meta_eval in metadata.iteritems():
                if not meta_eval(get_metadata(meta_name)):
                    break
            else:
                result[name] = trait
        return result

    @classmethod
    def class_filter(cls, **metadata):
        '''
        get a list of all the traits of this class

        @param **metadata: metadata to filter by

        This method a class method equivalent of the `traits` method.

        The traits returned know nothing about the values that Trait's
        instances are holding.

        This follows the same algorithm as traits does and does not allow for
        any simple way of specifying merely that A metadata name exists, but
        has any value.  This is because get_metadata returns None if A metadata
        key doesn't exist.
        '''
        return cls._filter(cls._classtraits, **metadata)

    @classmethod
    def class_names(cls, **metadata):
        '''
        get a list of all the names of this classes traits.

        @param **metadata: metadata to filter by

        This method is just like the :meth:`trait_names` method, but is unbound
        '''
        return cls.class_filter(**metadata).keys()

    def commit(self):
        '''commit changes'''
        self._sync.commit()
        self.sync()

    def members(self, **metadata):
        '''
        get trait list for class

        @param **metadata: metadata to filter by

        Returned TraitTypes know nothing about other values that any other of
        Trait's instances are holding.

        This follows the same algorithm as traits does and does not allow for
        any simple way of specifying merely that A metadata name exists, but
        has any value.  This is because get_metadata returns None if A metadata
        key doesn't exist.
        '''
        return self._filter(self._traits, **metadata)

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

    def names(self, **metadata):
        '''
        get all names of this instance's traits

        @param **metadata: metadata to filter by
        '''
        return self.members(**metadata).keys()

    def reset(self, labels=None, **metadata):
        '''
        @param labels: labels to search for (default: None)
        @param traits: list of strings naming trait attributes to reset

        Resets each of the traits whose names are specified in the traits
        list to their default values. If traits is None or omitted, the
        method resets all explicitly-defined object trait attributes to their
        default values. A list of attributes that the method was unable to
        reset, which is empty if all the attributes were successfully reset.
        '''
        if labels is None:
            labels = self.names(**metadata)
        this = self.this
        unresetable = []
        uappend = unresetable.append
        for label in labels:
            try:
                deleter(this, label)
            except (AttributeError, TraitError):
                uappend(label)
        return unresetable

    def set(self, notify=True, **traits):
        '''
        shortcut for setting object trait attributes

        @param notify: If True, then each value assigned may generate a
            trait change notification. If False, then no trait change
            notifications will be generated. (default: True)
        @param **traits: Trait attributes and their values to be set

        Treats each keyword argument to the method as the name of a trait
        attribute and sets the corresponding trait attribute to the value
        specified. This is a useful shorthand when a number of trait attributes
        need to be set on an object, or a trait attribute value needs to be set
        in a lambda function.
        '''
        this = self
        if not notify:
            this.A.events.enabled = False
            try:
                for name, value in traits.iteritems():
                    setter(this, name, value)
            finally:
                this.A.events.enabled = True
            return self
        for name, value in traits.iteritems():
            setter(this, name, value)
        return self

    def sync(self, **kw):
        '''synchronize traits with current instance property values'''
        cur = self._sync.current
        self.set(**dict((k, cur[k]) for k in self.names(**kw)))

    def update(self, **kw):
        '''update traits with new values'''
        self._sync.update_current(kw)

    def validate_many(self):
        '''validate model data'''
        for k, v in self._sync.current.iteritems():
            if not self.validate_one(k, v):
                return False
        return True

    def validate_one(self, trait, value):
        '''
        validate one trait

        @param trait: trait name
        @param value: value to validate
        '''
        try:
            # return if data is valid
            self._traits[trait].validate(trait, value)
            return True
        # return False if data is invalid
        except TraitError:
            return False
        # attributes are True if not specified
        except KeyError:
            return True


class _SimpleTest:

    '''simple test'''

    def __init__(self, value):
        self.value = value

    def __call__(self, test):
        return test == self.value

    def __repr__(self):
        return '<SimpleTest(%r)' % self.value

    def __str__(self):
        return self.__repr__()


__all__ = ['Traits', 'TraitSync']
