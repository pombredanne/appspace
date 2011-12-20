# -*- coding: utf-8 -*-

import sys
from types import ListType, TupleType

from stuf.utils import clsname

from appspace.utils import repr_type, class_of
from appspace.traits.error import TraitError

from .lang import Instance
from .base import TraitType

SequenceTypes = (ListType, TupleType, set, frozenset)


class Any(TraitType):

    default_value = None
    info_text = 'any value'


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
                clsname(self), default_value)
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

    '''instance of a python set.'''

    klass = set


class Tuple(Container):

    '''instance of a python tuple.'''

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
                clsname(self), default_value
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

    '''an instance of a python dictionary'''

    def __init__(self, default_value=None, allow_none=True, **md):
        '''
        create a dict trait type from a dict.

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
        
        
class Enum(TraitType):

    '''enum whose value must be in a given sequence.'''

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

    '''enum of strings that are caseless in validate.'''

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


class TCPAddress(TraitType):

    '''
    trait for an (ip, port) tuple.

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