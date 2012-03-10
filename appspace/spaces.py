# -*- coding: utf-8 -*-
'''appspace spaces'''

from functools import partial
from itertools import starmap

from stuf.six import items, strings
from stuf.utils import selfname, exhaust, twoway

from appspace.utils import lazyimport
from appspace.managers import Manager, StrictManager
from appspace.keys import ABranch, ANamespace, AApp, ifilter, appifies

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
        n = partial(manager.keyed, ANamespace)
        m = manager.set
        t = lambda x, y: y.build(manager) if (n(y) or b(y)) else m(x, y, l)
        t2 = cls._filter
        exhaust(starmap(t, ifilter(t2, items(vars(cls)))))
        return manager

    @staticmethod
    def factory(label, manager, *args):
        '''
        factory for manager

        @param label: label for manager
        '''
        # build manager
        manager = manager(label)
        mset = manager.set
        # register things in manager
        exhaust(starmap(mset, iter(args)))
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
        i = cls.include
        m = manager.set
        t = lambda x: not x[0].startswith('_') or isinstance(x[1], strings)
        t2 = lambda x, y: m(x, i(y))
        exhaust(starmap(t2, ifilter(t, items(vars(cls)))))

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
        m = manager.set
        n = partial(manager.keyed, ANamespace)
        t = lambda k, v: v.build(manager) if n(v) else m(k, v, label)
        t2 = cls._filter
        exhaust(starmap(t, ifilter(t2, items(vars(cls)))))


factory = Patterns.factory
include = Branch.include
patterns = Patterns.patterns
