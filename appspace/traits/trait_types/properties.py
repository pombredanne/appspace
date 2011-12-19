# -*- coding: utf-8 -*-
'''graph model properties'''

from __future__ import absolute_import

import sys

from .numbers import Int, Bool, Float as Ft
from .strings import Unicode, CheckedUnicode
from .base import NoDefaultSpecified, TraitType


class PropertyMixin(TraitType):

    '''property mixin'''

    metadata = dict(property=True)

    def __init__(self, initial=NoDefaultSpecified, **kw):
        kw.update(dict(property=True, indexed=kw.get('indexed', False)))
        super(PropertyMixin, self).__init__(initial, **kw)


class StringMixin(PropertyMixin):

    '''mixin for stringish properties'''

    def __init__(self, initial=NoDefaultSpecified, **kw):
        kw.update(dict(
            escaped=kw.get('escaped', False),
            slug_from=kw.get('slug_from', False)
        ))
        super(StringMixin, self).__init__(initial, **kw)


class BooleanField(PropertyMixin, Bool):

    '''boolean (maps onto Java boolean primitive)'''


class CharField(StringMixin, CheckedUnicode):

    '''checked string field'''

    def __init__(self, value='', minlen=0, maxlen=sys.maxint, regex='', **kw):
        super(CharField, self).__init__(value, minlen, maxlen, regex, **kw)


class FloatField(PropertyMixin, Ft):

    '''float field'''


class IntegerField(PropertyMixin, Int):

    '''integer field'''


class StringField(StringMixin, Unicode):

    '''string field'''


class TextField(StringField):

    '''string that can be full text searched'''

    def __init__(self, initial=NoDefaultSpecified, **kw):
        super(TextField, self).__init__(initial, **kw)
        kw.update(dict(full_text=kw.get('full_text', False)))
