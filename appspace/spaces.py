# -*- coding: utf-8 -*-
'''application builder'''

from __future__ import absolute_import

from stuf.utils import selfname

from .managers import Manager, appifies
from .keys import ABranch, ANamespace


class Patterns(object):

    '''patterns for manager configured by class'''

    _manager = Manager

    def __repr__(self):
        return str(self._gather())

    @classmethod
    def _gather(cls):
        this = list()
        tappend = this.append
        textend = this.extend
        # filters
        anamespace = ANamespace.implementedBy
        branch = ABranch.implementedBy
        for k, v in vars(cls).iteritems():
            # filter private and hidden
            if not k.startswith('_'):
                # handle namespace
                if anamespace(v):
                    textend(i for i in v.build())
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
        this = list()
        tappend = this.append
        textend = this.extend
        # filters
        anamespace = ANamespace.implementedBy
        branch = ABranch.implementedBy
        for k, v in vars(cls).iteritems():
            # filter private and hidden
            if not k.startswith('_'):
                # handle namespace
                if anamespace(v):
                    textend(i for i in v.build())
                # handle branches
                elif branch(v):
                    textend(v.build())
                # handle anything else
                else:
                    tappend((k, v))
        # build configuration
        return cls.patterns(selfname(cls), *tuple(cls._gather()))

    @classmethod
    def factory(label, manager, *args, **kw):
        '''
        factory for manager

        @param label: label for manager
        '''
        # build manager
        manager = manager(kw.get('module', 'appconf'))
        # register apps in manager
        apper = manager.set
        # add applications
        [apper(*arg) for arg in args]  # pylint: disable-msg=W0106
        apper(label, manager)
        return manager

    @classmethod
    def patterns(cls, label, *args, **kw):
        '''
        configure appspace

        @param label: name of branch appspace
        @param *args: tuple of module paths or component inclusions
        '''
        return cls.factory(label, cls._manager, *args, **kw)


@appifies(ABranch)
class Branch(object):

    '''branch configuration'''

    @classmethod
    def build(cls):
        '''gather branch configuration'''
        inc = cls.include
        return [
            (k, inc(v)) for k, v in vars(cls).iteritems()
            if all([not k.startswith('_'), isinstance(v, basestring)])
        ]

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
    def _pack(cls, this, that):
        '''build name'''
        return ('.'.join([selfname(cls), this]), that)

    @classmethod
    def build(cls):
        '''gather namespace configuration'''
        this = list()
        tappend = this.append
        textend = this.extend
        # filters
        anamespace = ANamespace.implementedBy
        pack = cls._pack
        for k, v in vars(cls).iteritems():
            if not k.startswith('_'):
                # handle namespaces
                if anamespace(v):
                    textend(pack(*i) for i in v.build())
                else:
                    tappend(pack(k, v))
        return this


factory = Patterns.factory
include = Branch.include
patterns = Patterns.patterns
__all__ = ('Branch', 'Namespace', 'Patterns', 'include', 'patterns')