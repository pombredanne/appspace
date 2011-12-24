# -*- coding: utf-8 -*-
'''trait properties'''

__all__ = [
    'TraitType', 'Bytes', 'CBytes', 'CUnicode', 'CheckedUnicode', 'List',
    'Container', 'CaselessStrEnum', 'Any', 'Tuple', 'Dict', 'ObjectName',
    'DottedObjectName', 'This', 'Instance', 'Type', 'Bool', 'CBool', 'Int',
    'Unicode', 'Undefined',
]

from .base import TraitType, Undefined
from .containers import (
    List, Container, CaselessStrEnum, Enum, Any, Tuple, Dict
)
from .lang import DottedObjectName, Instance, ObjectName, This, Type
from .strings import Bytes, CBytes, CUnicode, CheckedUnicode, Unicode
from .numbers import (
    Bool, CBool, CInt, CLong, CFloat, CComplex, Complex, Float, Int, Integer,
    Long,
)
