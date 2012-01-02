# -*- coding: utf-8 -*-
'''appspace extension utilities'''

from collections import Mapping, Sequence
from operator import attrgetter, itemgetter

from stuf.utils import getter

__all__ = ['itermembers', 'keyed', 'pluck', 'modname']


def itermembers(this):
    '''
    iterate over object members

    @param this: an object
    '''
    for key in dir(this):
        if not any([key.startswith('__'), key.isupper()]):
            try:
                value = getattr(this, key)
            except AttributeError:
                pass
            else:
                yield key, value


def keyed(key, this):
    '''
    check if item provides an app key

    @param label: app key
    @param this: object to check
    '''
    try:
        return key.providedBy(this)
    except (AttributeError, TypeError):
        try:
            return key.implementedBy(this)
        except (AttributeError, TypeError):
            return False


def modname(this):
    '''
    module name

    @param this: an object
    '''
    return getter(this, '__module__')


def pluck(key, data):
    '''
    fetch item from data structure by key

    @param key: label of item
    @param data: data containing item
    '''
    getit = itemgetter(key) if isinstance(
        data, (Mapping, Sequence)
    ) else attrgetter(key)
    try:
        return getit(data)
    except (AttributeError, IndexError):
        return None
