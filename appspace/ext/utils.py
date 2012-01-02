# -*- coding: utf-8 -*-
'''appspace extension utilities'''

from collections import Mapping, Sequence
from operator import attrgetter, itemgetter

from stuf.utils import getter

__all__ = ['itermembers', 'keyed', 'pluck', 'modname']


def itermembers(that):
    '''
    iterate object members

    @param this: an object
    @param predicate: filter for members (default: None)
    '''
    for key in dir(that):
        if not any([key.startswith('__'), key.isupper()]):
            try:
                value = getattr(that, key)
            except AttributeError:
                pass
            else:
                yield key, value


def keyed(key, item):
    '''
    check if item provides an app key

    @param label: app key
    @param item: item to check
    '''
    try:
        return key.providedBy(item[1])
    except (AttributeError, TypeError):
        try:
            return key.implementedBy(item[1])
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
    return item from data structure by key

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
