# -*- coding: utf-8 -*-
'''appspace spaces'''

from itertools import starmap

from stuf.six import items, strings
from stuf.utils import selfname, exhaust, twoway

from appspace.utils import lazy_import
from appspace.managers import Manager, StrictManager
from appspace.keys import ABranch, ANamespace, ifilter, appifies

__all__ = ('Branch', 'Namespace', 'Patterns', 'include', 'patterns')


class Patterns(object):

    '''patterns for manager configured by class'''

    strict = False

    @twoway
    def _manager(self):
        return StrictManager if self.strict else Manager

    @classmethod
    def build(cls):
        '''build manager configuration from class'''
        l = selfname(cls)
        manager = cls._manager(l)
        b = ABranch.implementedBy
        m = manager.set
        n = ANamespace.implementedBy
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
        apper = manager.set
        # register things in manager
        exhaust(starmap(apper, iter(args)))
        apper(label, manager)
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
            key = cls.key
            if isinstance(key, strings):
                key = lazy_import(key)
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
        n = ANamespace.implementedBy
        m = manager.set
        exhaust(starmap(
            lambda k, v: v.build(manager) if n(v) else m(k, v, label),
            ifilter(lambda x: not x[0].startswith('_'), items(vars(cls))),
        ))


factory = Patterns.factory
include = Branch.include
patterns = Patterns.patterns
