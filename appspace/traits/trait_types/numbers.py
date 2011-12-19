# -*- coding: utf-8 -*-
'''trait number types'''

from .base import TraitType


class Bool(TraitType):

    '''A boolean (True, False) trait.'''

    default_value = False
    info_text = 'a boolean'

    def validate(self, this, value):
        if isinstance(value, bool):
            return value
        self.error(this, value)


class CBool(Bool):

    '''casting version of the boolean trait.'''

    def validate(self, this, value):
        try:
            return bool(value)
        except:
            self.error(this, value)


class Int(TraitType):

    '''integer trait.'''

    default_value = 0
    info_text = 'an integer'

    def validate(self, this, value):
        if isinstance(value, int):
            return value
        self.error(this, value)


class CInt(Int):

    '''casting version of the int trait.'''

    def validate(self, this, value):
        try:
            return int(value)
        except:
            self.error(this, value)


class Integer(TraitType):

    '''
    integer trait.

    Longs that are unnecessary (<= sys.maxint) are cast to ints.
    '''

    default_value = 0
    info_text = 'an integer'

    def validate(self, obj, value):
        if isinstance(value, int):
            return value
        elif isinstance(value, long):
            # downcast longs that fit in int:
            # note that int(n > sys.maxint) returns a long, so
            # we don't need a condition on this cast
            return int(value)
        self.error(obj, value)


class Long(TraitType):

    '''long integer trait.'''

    default_value = 0L
    info_text = 'a long'

    def validate(self, this, value):
        if isinstance(value, long):
            return value
        if isinstance(value, int):
            return long(value)
        self.error(this, value)


class CLong(Long):

    '''casting version of long integer trait.'''

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

    '''casting version of float trait.'''

    def validate(self, this, value):
        try:
            return float(value)
        except:
            self.error(this, value)


class Complex(TraitType):

    '''trait for complex numbers.'''

    default_value = 0.0 + 0.0j
    info_text = 'a complex number'

    def validate(self, this, value):
        if isinstance(value, complex):
            return value
        if isinstance(value, (float, int)):
            return complex(value)
        self.error(this, value)


class CComplex(Complex):

    '''casting version of complex number trait.'''

    def validate(self, this, value):
        try:
            return complex(value)
        except:
            self.error(this, value)
