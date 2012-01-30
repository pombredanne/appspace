# -*- coding: utf-8 -*-
'''appspace builder'''

from __future__ import unicode_literals

from operator import contains

from appspace.spaces import patterns as apatterns
from appspace.keys import AAppspace, appifies, AppLookupError, NoAppError

__all__ = ['patterns']


@appifies(AAppspace)
class Appspace(object):

    '''appspace interface'''

    __slots__ = ['manager']

    def __init__(self, manager):
        '''
        init

        @param manager: appspace manager
        '''
        self.manager = manager

    def __getattr__(self, label):
        try:
            return object.__getattribute__(self, label)
        except AttributeError:
            return self.__getitem__(label)

    def __getitem__(self, label):
        try:
            return self.manager.get(label)
        except AppLookupError:
            raise NoAppError(label)

    def __call__(self, label, *args, **kw):
        try:
            result = self.__getitem__(label)
            return result(*args, **kw)
        except TypeError:
            return result

    def __contains__(self, label):
        return contains(self.manager, label)

    def __repr__(self):
        return repr(self.manager)


def patterns(label, *args, **kw):
    '''
    factory for manager

    @param label: label for manager
    '''
    manager = apatterns(label, *args, **kw)
    space = Appspace(manager)
    manager.set(label, space)
    return space


def class_patterns(label, clspatterns):
    '''
    factory for manager configured with class patterns

    @param label: label for manager
    @param clspatterns: class patterns
    '''
    manager = clspatterns.build()
    patterns = Appspace(manager)
    manager.set(label, patterns)
    return patterns
