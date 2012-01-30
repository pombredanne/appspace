# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from six import PY3

from appspace import patterns


PATTERNS = (
    ('square', 'math.sqrt'),
    ('fabulous', 'math.fabs'),
    ('formit', 're.match'),

)
if PY3:
    PATTERNS = PATTERNS + (
        ('store', 'collections.UserDict'),
        ('lower', 'string.ascii_lowercase'),
        ('upper', 'string.ascii_uppercase'),
    )
else:
    PATTERNS = PATTERNS + (
        ('store', 'UserDict.UserDict'),
        ('lower', 'string.lowercase'),
        ('upper', 'string.uppercase'),
    )

appconf = patterns('', *PATTERNS)
