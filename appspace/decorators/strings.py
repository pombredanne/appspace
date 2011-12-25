# -*- coding: utf-8 -*-
# pylint: disable-msg=w0702
'''
We should always be explicit about whether we're using bytes or unicode, both
for Python 3 conversion and for reliable unicode behaviour on Python 2. So
we don't have a Str type.
'''

from __future__ import absolute_import

import re
import sys

from .core import TraitType


class Bytes(TraitType):

    '''trait for strings.'''

    default_value = ''
    info_text = 'a string'

    def validate(self, this, value):
        if isinstance(value, bytes):
            return value
        self.error(this, value)


class CBytes(Bytes):

    '''casting version of string trait.'''

    def validate(self, this, value):
        try:
            return bytes(value)
        except:
            self.error(this, value)


class Unicode(TraitType):

    '''A trait for unicode strings.'''

    default_value = u''
    info_text = 'a unicode string'

    def validate(self, this, value):
        if isinstance(value, unicode):
            return value
        if isinstance(value, bytes):
            return unicode(value)
        self.error(this, value)


class CUnicode(Unicode):

    '''A casting version of the unicode trait.'''

    def validate(self, this, value):
        try:
            return unicode(value)
        except:
            self.error(this, value)


class CheckedUnicode(Unicode):

    '''
    Defines a trait whose value must be a Python string whose length is
    optionally in a specified range, and which optionally matches a specified
    regular expression.
    '''

    def __init__(self, value='', minlen=0, maxlen=sys.maxint, regex='', **md):
        '''
        Creates a String trait.

        Parameters
        ----------
        value : string
            The default value for the string
        minlen : integer
            The minimum length allowed for the string
        maxlen : integer
            The maximum length allowed for the string
        regex : string
            A Python regular expression that the string must match
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
        '''Returns a description of the trait.'''
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
        '''Validates that the value is a valid string'''
        return getattr(self, self._validate)(name, value)

    def validate_all(self, name, value):
        '''
        Validates that the value is a valid string in the specified length
        range which matches the specified regular expression.
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
        '''
        Validates that the value is a valid string in the specified length
        range
        '''
        try:
            value = super(CheckedUnicode, self).validate(value)
            if self.minlen <= len(value) <= self.maxlen:
                return value
        except:
            pass
        self.error(name, value)

    def validate_regex(self, name, value):
        '''
        Validates that the value is a valid string which matches the specified
        regular expression.
        '''
        try:
            value = super(CheckedUnicode, self).validate(value)
            if self.match(value) is not None:
                return value
        except:
            pass
        self.error(name, value)

    def validate_str(self, name, value):
        '''Validates that the value is a valid string'''
        try:
            return super(CheckedUnicode, self).validate(value)
        except:
            pass
        self.error(name, value)
