'''setup for appspace'''

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.util import setup

install_requires = ['zope.component>=3.10.0']
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    install_requires.append('importlib')
    install_requires.append('ordereddict')
    install_requires.append('unittest2')

setup(
    name='appspace',
    version='0.1.3',
    description='Loosely coupled application plumbing',
    long_description=open(os.path.join(os.getcwd(), 'README'), 'rb').read(),
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
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    install_requires=install_requires,
)
