# -*- coding: utf-8 -*-
'''appspace spaces'''

from functools import partial
from itertools import starmap

from stuf.six import strings
from stuf.utils import selfname, exhaust, exhaustmap, twoway

from appspace.utils import lazyimport
from appspace.managers import Manager, StrictManager
from appspace.keys import ABranch, ANamespace, AApp, appifies

__all__ = ('Branch', 'Namespace', 'Patterns', 'include', 'patterns')


class _Filter(object):

    @classmethod
    def _filter(self, x):
        return not x[0].startswith('_')


class Patterns(_Filter):

    '''patterns for manager configured by class'''

    key = AApp
    strict = False

    @twoway
    def _manager(self):
        '''manager class'''
        return StrictManager if self.strict else Manager

    @classmethod
    def build(cls):
        '''build manager configuration from class'''
        l = selfname(cls)
        # set key
        key = cls.key
        if isinstance(key, strings):
            # load key if string
            key = lazyimport(key)
        manager = cls._manager(l, key)  # pylint: disable-msg=e1121
        b = partial(manager.keyed, ABranch)
        m, n = manager.set, partial(manager.keyed, ANamespace)
        t = lambda x, y: y.build(manager) if (n(y) or b(y)) else m(y, x, l)
        exhaustmap(vars(cls), t, cls._filter)
        return manager

    @staticmethod
    def factory(label, manager, *args):
        '''
        factory for manager

        @param label: label for manager
        '''
        # build manager
        manager = manager(label)
        # register things in manager
        exhaust(starmap(lambda x, y: manager.set(y, x), iter(args)))
        return manager

    @classmethod
    def patterns(cls, label, *args):
        '''
        configure appspace

        @param label: name of branch appspace
        @param *args: tuple of module paths or component inclusions
        '''
        return cls.factory(label, cls._manager, *args)


class _PatternMixin(_Filter):

    @classmethod
    def _key(cls, label, manager):
        try:
            # lazily load key
            key = cls.key
            if isinstance(key, strings):
                key = lazyimport(key)
            # register class key
            manager.ez_register(ANamespace, label, key)
        except AttributeError:
            key = manager.key(ANamespace, label)


@appifies(ANamespace)
class Branch(_PatternMixin):

    '''branch configuration'''

    @classmethod
    def build(cls, manager):
        '''gather branch configuration'''
        cls._key(selfname(cls), manager)
        i, m = cls.include, manager.set
        t = lambda x: not x[0].startswith('_') or isinstance(x[1], strings)
        exhaustmap(vars(cls), lambda x, y: m(i(y), x), t)

    @staticmethod
    def include(module):
        '''
        configure branch appspace

        @param module: module import path
        '''
        return ('include', module)


@appifies(ANamespace)
class Namespace(_PatternMixin):

    '''configuration namespace'''

    @classmethod
    def build(cls, manager):
        '''gather namespace configuration'''
        label = selfname(cls)
        cls._key(label, manager)
        m, n = manager.set, partial(manager.keyed, ANamespace)
        t = lambda k, v: v.build(manager) if n(v) else m(v, k, label)
        exhaustmap(vars(cls), t, cls._filter)


factory = Patterns.factory
include = Branch.include
patterns = Patterns.patterns
