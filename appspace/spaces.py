# -*- coding: utf-8 -*-
'''appspace spaces'''

from collections import deque
from itertools import starmap

from stuf.utils import selfname
from stuf.six import items, strings

from appspace.managers import Manager, appifies
from appspace.keys import ABranch, ANamespace, ifilter

__all__ = ('Branch', 'Namespace', 'Patterns', 'include', 'patterns', 'key')


class Patterns(object):

    '''patterns for manager configured by class'''

    _manager = Manager

    def __repr__(self):
        return str(self._gather())

    @classmethod
    def _gather(cls):
        this = deque()
        tappend = this.append
        textend = this.extend
        # filters
        anamespace = ANamespace.implementedBy
        branch = ABranch.implementedBy
        # filter private and hidden
        test = lambda x: not x.startswith('_')
        for k, v in ifilter(test, items(vars(cls))):
            # handle namespace
            if anamespace(v):
                textend(iter(v.build()))
            # handle branches
            elif branch(v):
                textend(v.build())
            # handle anything else
            else:
                tappend((k, v))
        return this

    @classmethod
    def build(cls):
        '''build manager configuration from class'''
        this = deque()
        tappend = this.append
        textend = this.extend
        # filters
        anamespace = ANamespace.implementedBy
        branch = ABranch.implementedBy
        # filter private and hidden
        test = lambda x: not x.startswith('_')
        for k, v in ifilter(test, items(vars(cls))):
            # handle namespace
            if anamespace(v):
                textend(iter(v.build()))
            # handle branches
            elif branch(v):
                textend(v.build())
            # handle anything else
            else:
                tappend((k, v))
        # build configuration
        return cls.patterns(selfname(cls), *tuple(cls._gather()))

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
        list(starmap(apper, iter(args)))
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


@appifies(ABranch)
class Branch(object):

    '''branch configuration'''

    @classmethod
    def build(cls):
        '''gather branch configuration'''
        inc = cls.include
        test = lambda x, y: not x.startswith('_') or isinstance(y, strings)
        for v in ifilter(test, items(vars(cls))):
            yield v[0], inc(v[1])

    @staticmethod
    def include(module):
        '''
        configure branch appspace

        @param module: module import path
        '''
        return ('include', module)


@appifies(ANamespace)
class Namespace(object):

    '''configuration namespace'''

    @classmethod
    def build(cls):
        '''gather namespace configuration'''
        anamespace = ANamespace.implementedBy
        pack = lambda x, y: ('.'.join([selfname(cls), x]), y)
        test = lambda x: not x.startswith('_')
        for k, v in ifilter(test, items(vars(cls))):
            # handle namespaces
            if anamespace(v):
                for i in starmap(pack, iter(v.build())):
                    yield i
            else:
                yield pack(k, v)


factory = Patterns.factory
include = Branch.include
patterns = Patterns.patterns
