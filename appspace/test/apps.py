from appspace import patterns

apps = patterns(
    '',
    ('square', 'math.sqrt'),
    ('fabulous', 'math.fabs'),
    ('formit', 're.match'),
    ('lower', 'string.lowercase'),
    ('upper', 'string.uppercase'),
    ('store', 'UserDict.UserDict'),
)
