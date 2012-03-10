# -*- coding: utf-8 -*-
'''test appconf'''

from appspace import patterns

PATTERNS = (
    ('square', 'math.sqrt'),
    ('fabulous', 'math.fabs'),
    ('formit', 're.match'),
    ('mrk', 'math.isinf'),
    ('furf', 'math.isnan'),
    ('mrnrf', 'math.exp'),
)
appconf = patterns('', *PATTERNS)
