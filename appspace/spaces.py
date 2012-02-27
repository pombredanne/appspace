# -*- coding: utf-8 -*-
'''appspace spaces'''

from functools import partial
from itertools import starmap

from stuf.six import items, strings
from stuf.utils import selfname, exhaust, twoway

from appspace.utils import lazyimport
from appspace.managers import Manager, StrictManager
from appspace.keys import ABranch, ANamespace, ifilter, appifies, AApp

__all__ = ('Branch', 'Namespace', 'Patterns', 'include', 'patterns')


class Patterns(object):

    '''patterns for manager configured by class'''

    strict = False

    @twoway
    def _manager(self):
        # manager class
        return StrictManager if self.strict else Manager

    @classmethod
    def build(cls, key=AApp):
        '''build manager configuration from class'''
        l = selfname(cls)
        manager = cls._manager(l, key)  # pylint: disable-msg=e1121
        b = partial(manager.keyed, ABranch)
        m = manager.set
        n = partial(manager.keyed, ANamespace)
        exhaust(starmap(
            lambda x, y: y.build(manager) if n(y) or b(y) else m(x, y, l),
            ifilter(lambda x: not x[0].startswith('_'), items(vars(cls))),
        ))
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


class PatternMixin(object):

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
class Branch(PatternMixin):

    '''branch configuration'''

    @classmethod
    def build(cls, manager):
        '''gather branch configuration'''
        cls._key(selfname(cls), manager)
        test = lambda x: not x[0].startswith('_') or isinstance(x[1], strings)
        mset = manager.set
        inc = cls.include
        exhaust(starmap(
            lambda x, y: mset(x, inc(y)), ifilter(test, items(vars(cls))),
        ))

    @staticmethod
    def include(module):
        '''
        configure branch appspace

        @param module: module import path
        '''
        return ('include', module)


@appifies(ANamespace)
class Namespace(PatternMixin):

    '''configuration namespace'''

    @classmethod
    def build(cls, manager):
        '''gather namespace configuration'''
        label = selfname(cls)
        cls._key(label, manager)
        m = manager.set
        n = partial(manager.keyed, ANamespace)
        exhaust(starmap(
            lambda k, v: v.build(manager) if n(v) else m(k, v, label),
            ifilter(lambda x: not x[0].startswith('_'), items(vars(cls))),
        ))


factory = Patterns.factory
include = Branch.include
patterns = Patterns.patterns
