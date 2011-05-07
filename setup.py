'''setup for appspace'''

from setuptools import setup

setup(
    name='appspace',
    version='0.1',
    description='''Loosely coupled application plumbing''',
    long_description='''Loosely coupled application plumbing''',
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    license='ZPL',
    packages = ['appspace'],
    packages = ['appspace', 'appspace.test'],
    test_suite='appspace.test',
    zip_safe = False,
    keywords='component injection aspect-oriented spring',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ZPL License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = ['zope.component>=3.10.0']
)