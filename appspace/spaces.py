# -*- coding: utf-8 -*-
#pylint: disable-msg=w0106
'''appspace spaces'''

from functools import partial
from itertools import starmap

from stuf.six import items, strings
from stuf.utils import selfname, exhaust, twoway

from appspace.utils import lazy_import
from appspace.managers import Manager, StrictManager
from appspace.keys import ABranch, ANamespace, ifilter

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
        manager = cls._manager()
        m = manager.set
        n = ANamespace.implementedBy
        b = ABranch.implementedBy
        exhaust(starmap(
            lambda k, v: v.build(manager) if (n(v) or b(v)) else m(k, v),
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
        manager = manager()
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
        key = cls.key
        if isinstance(key, strings):
            key = lazy_import(key)
        manager.ez_register(ANamespace, label, key)


class Branch(PatternMixin):

    '''branch configuration'''

    @classmethod
    def build(cls, manager):
        '''gather branch configuration'''
        if cls.key:
            cls._key(selfname(cls), manager)
        test = lambda x, y: not x.startswith('_') or isinstance(y, strings)
        mset = manager.set
        inc = cls.include
        exhaust(starmap(
            lambda v: mset(v[0], inc(v[1])), ifilter(test, items(vars(cls))),
        ))

    @staticmethod
    def include(module):
        '''
        configure branch appspace

        @param module: module import path
        '''
        return ('include', module)


class Namespace(PatternMixin):

    '''configuration namespace'''

    @classmethod
    def build(cls, manager):
        '''gather namespace configuration'''
        label = selfname(cls)
        if cls.key:
            cls._key(label, manager)
        n = ANamespace.implementedBy
        m = partial(manager.set, key=label)
        exhaust(starmap(
            lambda k, v: v.build(manager) if n(v) else m(k, v),
            ifilter(lambda x: not x[0].startswith('_'), items(vars(cls))),
        ))


factory = Patterns.factory
include = Branch.include
patterns = Patterns.patterns
