# -*- coding: utf-8 -*-
'''traits classes'''

from __future__ import absolute_import

from inspect import isclass

from stuf import stuf
from stuf.utils import both, clsname, getcls, getter, deleter, setter

from appspace.keys import appifies
from appspace.ext import Sync, Synced

from .query import T
from .core import Trait
from .keys import ATraits
from .error import TraitError


class TraitSync(Sync):

    '''trait sync'''

    def __init__(self, original, **kw):
        super(TraitSync, self).__init__(original, **kw)
        self._traits = stuf()
        self._trait_values = stuf()

    def update_traits(self, kw):
        pass


class MetaTraits(type):

    '''makes sure Traits are instantiated with their name attribute set'''

    def __new__(cls, name, bases, classdict):
        '''
        new

        instantiate Traits in classdict, setting their name attribute
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

        finish initializing

        Sets this_class attribute of each Trait in the classdict to a newly
        created class.
        '''
        istrait = T.istrait
        cls._classtraits = classtraits = {}
        for k, v in classdict.iteritems():
            if istrait(k, v):
                v.this_class = cls
                classtraits[k] = v
        super(MetaTraits, cls).__init__(name, bases, classdict)


@appifies(ATraits)
class Traits(Synced):

    '''class with Traits'''

    __metaclass__ = MetaTraits

    _descriptor = Trait

    def __new__(cls, *args, **kw):
        '''
        new

        initalize Traits
        '''
        inst = super(Traits, cls).__new__(cls, *args, **kw)
        traits = inst._sync.update_traits
        istrait = T.istrait
        # set all Trait instances to their default values
        for k, v in vars(cls).iteritems():
            if istrait(k, v):
                v.instance_init(inst)
                traits(k, v)
        return inst

    @both
    def C(self):
        '''local settings'''
        return T(self).localize().one()

    @classmethod
    def class_members(cls, **metadata):
        '''
        get a list of Traits

        @param **metadata: metadata to filter by

        This method is the class method equivalent of the members method.

        The traits returned know nothing about the values that Traits are
        holding.

        This does not allow for any simple way of specifying merely that a
        metadata name exists but has any value. This is because get_metadata
        returns None if a metadata key doesn't exist.
        '''
        return T.traits(cls._classtraits, **metadata)

    @classmethod
    def class_names(cls, **metadata):
        '''
        get a list of all the names of this classes traits.

        @param **metadata: metadata to filter by

        This method is just like the 'names' method but is unbound
        '''
        return cls.class_members(**metadata).keys()

    def commit(self):
        '''commit changes'''
        self._sync.commit()
        self.sync()

    def members(self, **metadata):
        '''
        get Trait list for class

        @param **metadata: metadata to filter by

        Traits know nothing about the values of other Traits.

        This doesn't allow for any simple way of specifying merely that a
        metadata name exists but has any value. This is because get_metadata
        returns None if a metadata key doesn't exist.
        '''
        return T.traits(self._sync.traits, **metadata)

    def metadata(self, label, key):
        '''
        get metadata values for Trait by key

        @param label: Trait label
        @param key: key in Trait metadata
        '''
        try:
            return getter(getcls(self.this), label).get_metadata(key)
        except AttributeError:
            raise TraitError(
                '%s has no Trait %s' % (clsname(self.this), label)
            )

    def names(self, **metadata):
        '''
        get all names of this instance's Traits

        @param **metadata: metadata to filter by
        '''
        return self.members(**metadata).keys()

    def reset(self, labels=None, **metadata):
        '''
        @param labels: labels to search for (default: None)
        @param metadata: list of strings naming Traits to reset

        Resets each Trait named by the 'labels' argument to its default values.
        If that argument is None or left out, all Traits are reset to their
        default values. The list of Traits that the method was unable to reset
        will be empty if all Traits were successfully reset.
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
        shortcut for setting Traits

        @param notify: If True, then each value assigned may generate an event.
        If False, then no event is generated. (default: True)
        @param **traits: Trait and values

        Treats each keyword argument as a Trait name and sets the Trait to the
        value specified. This is a useful shorthand when a number of Traits
        need to be set on an object or a Trait value needs to be set with a
        lambda function.
        '''
        this = self
        if not notify:
            T(this).enabled = False
            try:
                for name, value in traits.iteritems():
                    setter(this, name, value)
            finally:
                T(this).enabled = True
            return self
        for name, value in traits.iteritems():
            setter(this, name, value)
        return self

    def sync(self, **kw):
        '''synchronize traits with current instance property values'''
        t = self._sync.traits
        self.set(**dict((k, t[k]) for k in self.names(**kw)))

    def update(self, **kw):
        '''update traits with new values'''
        self._sync.update_traits(kw)

    def validate_many(self):
        '''validate all Trait values'''
        for k, v in self._sync.traits.iteritems():
            if not self.validate_one(k, v):
                return False
        return True

    def validate_one(self, trait, value):
        '''
        validate one trait

        @param trait: Trait name
        @param value: value to validate
        '''
        # return if data is valid
        try:
            self._sync.traits[trait].validate(trait, value)
            return True
        # return False if data is invalid
        except TraitError:
            return False
        # attributes are True if not specified
        except KeyError:
            return True


__all__ = ['Traits', 'TraitSync']
