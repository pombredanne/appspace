# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''traits keys'''

from __future__ import absolute_import

from appspace.keys import AppspaceKey, Attribute


class ATrait(AppspaceKey):

    '''trait property key'''

    default_value = Attribute('Trait default value')
    info_text = Attribute('Trait information text')
    metadata = Attribute('Trait metadata')
    name = Attribute('Trait name')
    this_class = Attribute('class pointer')

    def error(this, value):
        '''
        handle Trait errors

        @param this: instance
        @param value: incorrect value
        '''

    def get_default_value():
        '''create a new instance with default value'''

    def get_metadata(key):
        '''
        get metadata

        @param key: metadata key
        '''

    def info():
        '''information text'''

    def instance_init(value):
        '''
        called by Traits.__new__ to finish init'ing instance

        @param value: newly created parent Traits instance

        Some stages of initialization must be delayed until the parent instance
        has been created. This method is called in Traits.__new__ after the
        instance has been created.

        This method triggers the creation and validation of default values and
        also things like the resolution of string class names in the Type or
        Instance class.
        '''

    def set_default_value(trait):
        '''
        set the default Trait value on a per instance basis

        @param trait: a Trait

        This method is called by instance_init to create and validate the
        default value. The creation and validation of default values must be
        delayed until the class has been instantiated.
        '''

    def set_metadata(key, value):
        '''
        set trait metadata

        @param key: metadata key
        @param value: metadata value
        '''


class ATraits(AppspaceKey):

    '''Traits property key'''

    def C():
        '''local settings'''

    def class_members(**metadata):
        '''
        get Trait list for class

        @param **metadata: metadata to filter by

        This method is the class method equivalent of the members method.

        The Traits returned know nothing about values that other Traits hold.
        This does not allow for any simple way of specifying merely that a
        metadata name exists but has any value. This is because get_metadata
        returns None if a metadata key doesn't exist.
        '''

    def class_names(**metadata):
        '''
        get a list of all the names of this classes traits.

        @param **metadata: metadata to filter by

        This method is just like the 'names' method but is unbound
        '''

    def commit():
        '''commit changes'''

    def members(**metadata):
        '''
        get a list of Traits

        @param **metadata: metadata to filter by

        Traits know nothing about the values of other Traits.

        This doesn't allow for any simple way of specifying merely that a
        metadata name exists but has any value. This is because get_metadata
        returns None if a metadata key doesn't exist.
        '''

    def metadata(label, key):
        '''
        get metadata values for Trait by key

        @param label: Trait label
        @param key: key in Trait metadata
        '''

    def names(**metadata):
        '''
        get all names of this instance's Traits

        @param **metadata: metadata to filter by
        '''

    def reset(labels=None, **metadata):
        '''
        @param labels: labels to search for (default: None)
        @param metadata: list of strings naming Traits to reset

        Resets each Trait named by the 'labels' argument to its default values.
        If that argument is None or left out, all Traits are reset to their
        default values. The list of Traits that the method was unable to reset
        will be empty if all Traits were successfully reset.
        '''

    def set(notify=True, **traits):
        '''
        shortcut for setting Traits

        @param notify: whether to generate an event (default: True)
        @param **traits: Trait and values

        Treats each keyword argument as a Trait name and sets the Trait to the
        value specified. This is a useful shorthand when a number of Traits
        need to be set on an object or a Trait's value needs to be set with a
        lambda function.
        '''

    def update(**kw):
        '''update Traits with new values'''

    def validate_many():
        '''validate all Trait values'''

    def validate_one(trait, value):
        '''
        validate one Trait

        @param trait: Trait name
        @param value: value to validate
        '''


__all__ = ['ATrait', 'ATraits']
