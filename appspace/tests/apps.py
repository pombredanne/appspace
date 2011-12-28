# -*- coding: utf-8 -*-

from __future__ import absolute_import

from manager import patterns

appconf = patterns(
    '',
    ('square', 'math.sqrt'),
    ('fabulous', 'math.fabs'),
    ('formit', 're.match'),
    ('lower', 'string.lowercase'),
    ('upper', 'string.uppercase'),
    ('store', 'UserDict.UserDict'),
)
