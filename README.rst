*appspace* is a component injection framework that allows any mishmash of Python 
classes, objects, functions, or modules to be loosely cobbled together into an 
application. 

An *appspace* application is built with an appconf (application configuration) 
similar to a Django urlconf:

>>> from appspace import patterns
>>> apps = patterns(
...    'helpers',
...    ('square', 'math.sqrt'),
...    ('fabulous', 'math.fabs'),
...    include('subapp', 'foo.bar')
... )

Once configured, application components can be accessed as object attributes,
dictionary keys, or by calling the component manager directly:

>>> fab1 = plug.helpers.fabulous
>>> fab2 = plug['helpers']['fabulous']
>>> fab1(2)
2.0
>>> fab2(2)
2.0
>>> plug.helpers.fabulous(2)
2.0
>>> plug('fabulous', 2)
2.0