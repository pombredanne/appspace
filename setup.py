# -*- coding: utf-8 -*-
'''setup for appspace'''

from __future__ import absolute_import

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_requires = ['zope.interface>=3.8.0', 'stuf>=0.8.1', 'six>=1.1.0']
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    install_requires.extend(['importlib'])

setup(
    name='appspace',
    version='0.5.0',
    description='easy application construction with easy building blocks',
    long_description=open(os.path.join(os.getcwd(), 'README.rst'), 'r').read(),
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    license='MIT',
    url='https://bitbucket.org/lcrees/appspace',
    packages=['appspace'],
    test_suite='appspace.tests',
    zip_safe=False,
    keywords='component architecture injection aspect-oriented',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    install_requires=install_requires,
)
