#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''setup for appspace'''

import sys
from os import getcwd
from os.path import join
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
from appspace import __version__

install_requires = list(l for l in open(
    join(getcwd(), 'requirements.txt'), 'r',
).readlines())
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    install_requires.extend(['importlib'])

setup(
    name='appspace',
    version='{}.{}.{}'.format(*__version__),
    description='easy application construction with easy building blocks',
    long_description=open(os.path.join(os.getcwd(), 'README.rst'), 'r').read(),
    keywords='component architecture injection aspect-oriented',
    license='BSD',
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='https://bitbucket.org/lcrees/appspace',
    packages=['appspace'],
    test_suite='appspace.tests',
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
