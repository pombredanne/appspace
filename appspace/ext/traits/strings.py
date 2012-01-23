# -*- coding: utf-8 -*-
# pylint: disable-msg=w0702
'''
stringy traits

We should always be explicit about whether we're using bytes or unicode, both
for Python 3 conversion and for reliable unicode behavior on Python 2. So we
don't have a Str type.
'''

from __future__ import absolute_import

import re
import sys
from inspect import ismodule

from .core import Trait


class Bytes(Trait):

    '''trait for strings'''

    default_value = ''
    info_text = 'a string'

    def validate(self, this, value):
        if isinstance(value, bytes):
            return value
        self.error(this, value)


class CBytes(Bytes):

    '''casting version of string trait'''

    def validate(self, this, value):
        try:
            return bytes(value)
        except:
            self.error(this, value)


class Unicode(Trait):

    '''trait for unicode strings'''

    default_value = u''
    info_text = 'a unicode string'

    def validate(self, this, value):
        if isinstance(value, unicode):
            return value
        if isinstance(value, bytes):
            return unicode(value)
        self.error(this, value)


class CUnicode(Unicode):

    '''casting version of the unicode trait'''

    def validate(self, this, value):
        try:
            return unicode(value)
        except:
            self.error(this, value)


class CheckedUnicode(Unicode):

    '''
    trait whose value must be a Python string whose length is optionally in a
    specified range, and which optionally matches a specified regular
    expression
    '''

    def __init__(self, value='', minlen=0, maxlen=sys.maxint, regex='', **md):
        '''
        @param value: default value for the string
        @param minlen: minimum length allowed for the string
        @param maxlen : maximum length allowed for the string
        @param regex: regular expression that the string must match
        '''
        super(CheckedUnicode, self).__init__(value, **md)
        self.minlen = max(0, minlen)
        self.maxlen = max(self.minlen, maxlen)
        self.regex = regex
        self._validate = 'validate_all'
        if self.regex != '':
            self.match = re.compile(self.regex).match
            if self.minlen == 0 and self.maxlen == sys.maxint:
                self._validate = 'validate_regex'
        elif self.minlen == 0 and self.maxlen == sys.maxint:
            self._validate = 'validate_str'
        else:
            self._validate = 'validate_len'

    def info(self):
        '''trait description'''
        msg = ''
        if self.minlen != 0 and self.maxlen != sys.maxint:
            msg = ' between %d and %d characters long' % (
                self.minlen, self.maxlen
            )
        elif self.maxlen != sys.maxint:
            msg = ' <= %d characters long' % self.maxlen
        elif self.minlen != 0:
            msg = ' >= %d characters long' % self.minlen
        if self.regex != '':
            if msg != '':
                msg += ' and'
            msg += (' matching the pattern %s' % self.regex)
        return 'a string' + msg

    def validate(self, name, value):
        '''validates value is valid string'''
        return getattr(self, self._validate)(name, value)

    def validate_all(self, name, value):
        '''
        validates value is valid string in the specified length range which
        matches the specified regular expression
        '''
        try:
            value = super(CheckedUnicode, self).validate(value)
            if all([
                self.minlen <= len(value) <= self.maxlen,
                self.match(value) is not None,
            ]):
                return value
        except:
            pass
        self.error(name, value)

    def validate_len(self, name, value):
        '''validates value is valid string within specified length range'''
        try:
            value = super(CheckedUnicode, self).validate(value)
            if self.minlen <= len(value) <= self.maxlen:
                return value
        except:
            pass
        self.error(name, value)

    def validate_regex(self, name, value):
        '''
        validates value is valid string that matches the specified regular
        expression
        '''
        try:
            value = super(CheckedUnicode, self).validate(value)
            if self.match(value) is not None:
                return value
        except:
            pass
        self.error(name, value)

    def validate_str(self, name, value):
        '''validates value is a valid string'''
        try:
            return super(CheckedUnicode, self).validate(value)
        except:
            pass
        self.error(name, value)


__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
