# -*- coding: utf-8 -*-
'''traits classes'''

from __future__ import absolute_import

from inspect import isclass

from stuf import stuf
from stuf.utils import both, clsname, getcls, lazy

from appspace.keys import appifies
from appspace.composer import Sync, Synced

from .query import T
from .core import Trait
from .keys import ATraits
from .error import TraitError


class TraitSync(Sync):

    '''trait sync'''

    def __init__(self, original, **kw):
        '''
        init

        @param original: original data
        @param **kw: any updated data
        '''
        super(TraitSync, self).__init__(original, **kw)
        # traits
        self.traits = stuf()

    def update_traits(self, kw):
        '''
        update current data

        @param kw: keyword arguments
        '''
        self.traits.update(kw)
        # update current
        self.current.update(kw)
        # update changed data reference
        self.changed.update(kw)
        # flag as modified
        self.modified = True


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
    _syncer = TraitSync

    def __new__(cls, *args, **kw):
        '''
        new

        initalize Traits
        '''
        inst = super(Traits, cls).__new__(cls, *args, **kw)
        # set all Traits to their default values
        cls._trait_values = {}
        cls._trait_errors = {}
        for v in cls._classtraits.itervalues():
            v.instance_init(inst)
        return inst

    @lazy
    def _query(self):
        return T(self)

    @lazy
    def _sync(self):
        '''sync provider'''
        # initialize with any arguments
        sync = self._syncer(self._element(self), **self._attrs)
        # initialize with default Trait values
        sync.traits.update(self._trait_values)
        # sync with any Trait values passes as arguments
        current = sync.current
        sync.traits.update((k, current[k]) for k in self._classtraits.keys())
        return sync

    @both
    def C(self):
        '''local settings'''
        return T(self).localize().one()

    @classmethod
    def class_members(cls, **metadata):
        '''
        get Trait list for class

        @param **metadata: metadata to filter by

        This method is the class method equivalent of the members method.

        The Traits returned know nothing about values that other Traits hold.
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

    def members(self, **metadata):
        '''
        get a list of Traits

        @param **metadata: metadata to filter by

        Traits know nothing about the values of other Traits.

        This doesn't allow for any simple way of specifying merely that a
        metadata name exists but has any value. This is because get_metadata
        returns None if a metadata key doesn't exist.
        '''
        return self._query.traits(self._sync.traits, **metadata)

    def metadata(self, label, key):
        '''
        get metadata values for Trait by key

        @param label: Trait label
        @param key: key in Trait metadata
        '''
        try:
            return getattr(getcls(self.this), label).get_metadata(key)
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
                delattr(this, label)
            except (AttributeError, TraitError):
                uappend(label)
        return unresetable

    def set(self, notify=True, **traits):
        '''
        shortcut for setting Traits

        @param notify: whether to generate an event (default: True)
        @param **traits: Trait and values

        Treats each keyword argument as a Trait name and sets the Trait to the
        value specified. This is a useful shorthand when a number of Traits
        need to be set on an object or a Trait's value needs to be set with a
        lambda function.
        '''
        setr = setattr
        if not notify:
            T(self).enabled = False
            try:
                for k, v in traits.iteritems():
                    setr(self, k, v)
            finally:
                T(self).enabled = True
            return self
        for k, v in traits.iteritems():
            setr(self, k, v)
        return self

    def update(self, **kw):
        '''update Traits with new values'''
        self._sync.update_traits(kw)

    def validate_many(self):
        '''validate all Trait values'''
        validate_one = self.validate_one
        validations = list()
        for k, v in self._sync.traits.iteritems():
            validations.append(validate_one(k, v))
        return all(validations)

    def validate_one(self, trait, value):
        '''
        validate one Trait

        @param trait: Trait name
        @param value: value to validate
        '''
        # return if data is valid
        try:
            self._classtraits[trait].validate(trait, value)
            return True
        # return False if data is invalid
        except TraitError, e:
            self._trait_errors[trait] = e
            return False
        # attributes are True if not specified
        except KeyError:
            return True


__all__ = ['Traits', 'TraitSync']
