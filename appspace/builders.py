# -*- coding: utf-8 -*-
'''appspace builder'''

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
            item = self.manager.get(label, self.manager._current)
            self.manager._current = self.manager._root
            return item
        except AppLookupError:
            try:
                self.manager.namespace(label)
            except AppLookupError:
                raise NoAppError(label)
            else:
                self.manager._current = label
                return self

    def __call__(self, label, *args, **kw):
        try:
            result = self.__getitem__(label)
            return result(*args, **kw)
        except TypeError:
            return result

    def __repr__(self):
        return repr(self.manager)


def patterns(label, *args, **kw):
    '''
    factory for manager

    @param label: label for manager
    '''
    return Appspace(apatterns(label, *args, **kw))


def class_patterns(clspatterns):
    '''
    factory for manager configured with class patterns

    @param label: label for manager
    @param clspatterns: class patterns
    '''
    return Appspace(clspatterns.build())
