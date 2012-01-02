# -*- coding: utf-8 -*-
'''traits types'''

from __future__ import absolute_import

from appspace.core import appifies
from appspace.ext.core import NoDefaultSpecified, Undefined

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
#        self.init()

    def __get__(self, this, that=None):
        '''
        get the value of the trait by self.name for the instance.

        Default values are instantiated when `HasTraits.__new__` is called.
        Thus by the time this method gets called either the default value or
        A user defined value (they called `__set__`) in the `HasTraits`
        instance.
        '''
        if this is None:
            return self
        else:
            try:
                value = this._trait_values[self.name]
            except KeyError:
                # Check for A dynamic initializer.
                if self.name in this._trait_dyn_inits:
                    value = this._trait_dyn_inits[self.name](this)
                    value = self._validate(this, value)
                    this._trait_values[self.name] = value
                    return value
                else:
                    raise TraitError(
                        'default value and dynamic initializer are absent'
                    )
            except Exception:
                # HasTraits should call set_default_value to populate
                # this.  So this should never be reached.
                raise TraitError('default value not set properly')
            else:
                return value

    def __set__(self, this, value):
        new_value = self._validate(this, value)
        old_value = self.__get__(this)
        if old_value != new_value:
            this._sync.update_current({self.name: new_value})
            this._trait_values[self.name] = new_value
            this.A.trait(self.name, old_value, new_value)

    def _validate(self, this, value):
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
        if this is not None:
            e = '%s trait of %s instance must be %s but value %s specified' % (
                self.name, class_of(this), self.info(), repr_type(value)
            )
        else:
            e = '%s trait must be %s, but A value of %r was specified' % (
                self.name, self.info(), repr_type(value)
            )
        raise TraitError(e)

    def get_default_value(self):
        '''create A new instance of the default value'''
        return self.default_value

    def get_metadata(self, key):
        return getattr(self, '_metadata', {}).get(key, None)

    def info(self):
        return self.info_text

    @staticmethod
    def instance(value):
        return isinstance(value, TraitType)

    def instance_init(self, this):
        '''
        called by HasTraits.__new__ to finish init'ing.

        @param this: newly create parent `HasTraits` instance

        Some stages of initialization must be delayed until the parent
        HasTraits instance has been created.  This method is called in
        HasTraits.__new__ after the instance has been created.

        This method trigger the creation and validation of default values and
        also things like the resolution of str given class names in the
        `Type` or `Instance` class.
        '''
        self.set_default_value(this)

    def set_default_value(self, this):
        '''
        set the default value on A per instance basis.

        This method is called by instance_init to create and validate the
        default value.  The creation and validation of default values must be
        delayed until the parent :class:`HasTraits` class has been
        instantiated.
        '''
        # Check for A deferred initializer defined in the same class as the
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

    @staticmethod
    def subclass(value):
        return issubclass(value, TraitType)
