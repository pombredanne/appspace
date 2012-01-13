# -*- coding: utf-8 -*-
'''trait types'''

from __future__ import absolute_import

from appspace.ext import __
from appspace.keys import appifies
from appspace.ext.keys import NoDefault, Undefined

from .keys import ATraitType
from .error import TraitError
from .utils import class_of, repr_type


class TraitType(object):

    '''base class for all traits'''

    appifies(ATraitType)

    default_value = Undefined
    info_text = 'any value'
    metadata = {}
    name = ''
    this_class = ''

    def __init__(self, default_value=NoDefault, **metadata):
        '''
        init

        @param default_value: default trait value (default: NoDefault)
        '''
        if default_value is not NoDefault:
            self.default_value = default_value
        self._metadata = self.metadata.copy()
        if metadata:
            self._metadata.update(metadata)

    def __get__(self, this, that=None):
        '''
        get the value of the trait by self.name for the instance

        Default values are instantiated when `Traits.__new__` is called.
        Thus by the time this method gets called either the default value or
        a user defined value (they called `__set__`) in the `Traits`
        instance.
        '''
        if this is None:
            return self
        sync = this._sync
        try:
            value = sync._traits[self.name]
        except KeyError:
            # Check for a dynamic initializer.
            if self.name in this._trait_dyn_inits:
                value = this._trait_dyn_inits[self.name](this)
                value = self._validate(this, value)
                sync.update_traits({self.name: value})
                return value
            else:
                raise TraitError(
                    'default value and dynamic initializer are absent'
                )
        except:
            # Traits should call set_default_value to populate this. So this
            # should never be reached.
            raise TraitError('default value not set properly')
        else:
            return value

    def __set__(self, this, value):
        # validate new value
        new_value = self._validate(this, value)
        # fetch old value
        old_value = self.__get__(this)
        # if changed...
        if old_value != new_value:
            name = self.name
            this._sync.update_traits({name: new_value})
            __(this).trait(name, old_value, new_value)

    def _validate(self, this, value):
        # valideate value "this"
        if hasattr(self, 'validate'):
            return self.validate(this, value)
        elif hasattr(self, 'is_valid_for'):
            if self.is_valid_for(value):
                return value
            raise TraitError('invalid value for type: %r' % value)
        elif hasattr(self, 'value_for'):
            return self.value_for(value)
        return value

    def error(self, this, value):
        '''
        handle value errors

        @param this: instance
        @param value: incorrect value
        '''
        if this is not None:
            e = '%s trait of %s instance must be %s but value %s specified' % (
                self.name, class_of(this), self.info(), repr_type(value)
            )
        else:
            e = '%s trait must be %s, but a value of %r was specified' % (
                self.name, self.info(), repr_type(value)
            )
        raise TraitError(e)

    def get_default_value(self):
        '''create a new instance of the default value'''
        return self.default_value

    def get_metadata(self, key):
        '''
        get metadata

        @param key: metadata key
        '''
        return getattr(self, '_metadata', {}).get(key, None)

    def info(self):
        '''information text'''
        return self.info_text

    def instance_init(self, value):
        '''
        called by Traits.__new__ to finish init'ing instance

        @param value: newly create parent `Traits` instance

        Some stages of initialization must be delayed until the parent
        Traits instance has been created.  This method is called in
        Traits.__new__ after the instance has been created.

        This method trigger the creation and validation of default values and
        also things like the resolution of str given class names in the Type or
        Instance class.
        '''
        self.set_default_value(value)

    def set_default_value(self, value):
        '''
        set the default value on a per instance basis

        @param value: a value

        This method is called by instance_init to create and validate the
        default value. The creation and validation of default values must be
        delayed until the Traits class has been instantiated.
        '''
        # Check for A deferred initializer defined in the same class as the
        # trait declaration or above.
        mro = type(value).mro()
        cls = None
        name = self.name
        meth_name = '_{name}_default'.format(name=name)
        for cls in mro[:mro.index(self.this_class) + 1]:
            if meth_name in cls.__dict__:
                break
        else:
            # We didn't find one. Do static initialization.
            dv = self.get_default_value()
            newdv = self._validate(value, dv)
            value._sync.update_traits({name: newdv})
            return
        # Complete the dynamic initialization.
        value._trait_dyn_inits[name] = cls.__dict__[meth_name]

    def set_metadata(self, key, value):
        '''
        set metadata

        @param key: metadata key
        @param value: metadata value
        '''
        getattr(self, '_metadata', {})[key] = value
