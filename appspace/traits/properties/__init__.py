# -*- coding: utf-8 -*-
'''trait properties'''

__all__ = [
    'TraitType', 'Bytes', 'CBytes', 'CUnicode', 'CheckedUnicode', 'ListType',
    'Container', 'CaselessStrEnum', 'Any', 'Tuple', 'Dict', 'ObjectName',
    'DottedObjectName', 'This', 'Instance', 'Type', 'Bool', 'CBool', 'Int',
]

from .base import TraitType
from .strings import Bytes, CBytes, CUnicode, CheckedUnicode
from .containers import (
    ListType, Container, CaselessStrEnum, Enum, Any, Tuple, Dict
)
from .lang import DottedObjectName, Instance, ObjectName, This, Type
from .numbers import (
    Bool, CBool, CInt, CLong, CFloat, CComplex, Complex, Float, Int, Integer,
    Long,
)
