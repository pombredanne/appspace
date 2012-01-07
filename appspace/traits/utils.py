# -*- coding: utf-8 -*-
'''appspace trait utilities'''

from types import InstanceType
from stuf.utils import clsname, getter

from appspace.utils import getcls


def add_article(name):
    '''
    get string containing the correct indefinite article ('a' or 'an') prefixed
    to the specified string
    '''
    return 'an ' + name if name[:1].lower() in 'aeiou' else 'a ' + name


def class_of(this):
    '''
    get string containing class name of object with the correct indefinite
    article ('a' or 'an') preceding it
    '''
    if isinstance(this, basestring):
        return add_article(this)
    return add_article(clsname(this))


def get_members(this, predicate=None):
    '''
    version of inspect.getmembers that handles missing attributes.

    This is useful when there are descriptor based attributes that for some
    reason raise AttributeError even though they exist.
    '''
    results = []
    rappend = results.append
    for key in dir(this):
        try:
            value = getter(this, key)
        except AttributeError:
            pass
        else:
            if not predicate or predicate(value):
                rappend((key, value))
    results.sort()
    return results


def repr_type(this):
    '''
    return a string representation of a value and its type for readable error
    messages

    @param this: value to probe
    '''
    the_type = type(this)
    if the_type is InstanceType:
        # Old-style class.
        the_type = getcls(this)
    return '%r %r' % (this, the_type)
