'''setup - setuptools based setup for tubing'''

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='appspace',
    version='0.1',
    description='''Loose coupled Python application plumbing''',
    long_description='''Loose coupled Python application plumbing''',
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    license='ZPL',
    packages = ['appspace'],
    packages = ['appspace', 'appspace.test'],
    test_suite='appspace.test',
    zip_safe = False,
    keywords='application composition component injection aspect-oriented spring',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ZPL License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = ['zope.component>=3.10.0']
)