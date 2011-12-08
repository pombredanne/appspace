*appspace* is a component injection framework that allows any mishmash of Python 
classes, objects, functions, or modules to be dynamically cobbled together into 
an application. 

An appspaced application is built with an appconf (application configuration) 
similar to a Django urlconf:

>>> from appspace import patterns
>>> appconf = patterns(
...    'helpers',
...    ('square', 'math.sqrt'),
...    ('fabulous', 'math.fabs'),
...    include('subapp', 'foo.bar.apps')
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