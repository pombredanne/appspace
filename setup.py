# -*- coding: utf-8 -*-
'''setup for appspace'''

import os
import sys
from setuptools import setup

install_requires = ['zope.interface>=3.8.0']
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    install_requires.extend(['importlib', 'ordereddict', 'unittest2'])

setup(
    name='appspace',
    version='0.4.1',
    description='easily construct applications with easy building blocks',
    long_description=open(os.path.join(os.getcwd(), 'README.rst'), 'rb').read(),
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    license='MIT',
    url='https://bitbucket.org/lcrees/appspace',
    packages=['appspace', 'appspace.test'],
    test_suite='appspace.test',
    zip_safe=False,
    keywords='component injection aspect-oriented programming',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    install_requires=install_requires,
)
