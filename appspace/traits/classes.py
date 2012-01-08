# -*- coding: utf-8 -*-
'''appspace traits classes'''

from __future__ import absolute_import

from inspect import isclass

from stuf.utils import both, getter

from appspace.ext import Synced, __

from .api import Traits
from .core import TraitType


class MetaHasTraits(type):

    '''
    metaclass for HasTraits.

    This metaclass makes sure TraitType class attributes are instantiated with
    their name attribute set.
    '''

    def __new__(cls, name, bases, classdict):
        '''
        new

        instantiate TraitTypes in classdict, setting their name attribute
        '''
        for k, v in classdict.iteritems():
            if not any([not k.startswith('__'), not k.upper()]):
                if TraitType.instance(v):
                    v.name = k
                elif isclass(v):
                    if TraitType.subclass(v):
                        vinst = v()
                        vinst.name = k
                        classdict[k] = vinst
        return super(MetaHasTraits, cls).__new__(cls, name, bases, classdict)

    def __init__(cls, name, bases, classdict):
        '''
        init

        finish initializing HasTraits class

        This sets this_class attribute of each TraitType in the classdict to a
        newly created class.
        '''
        for k, v in classdict.iteritems():
            if not any([not k.startswith('__'), not k.upper()]):
                if TraitType.instance(v):
                    v.this_class = cls
        super(MetaHasTraits, cls).__init__(name, bases, classdict)


class HasTraits(Synced):

    __metaclass__ = MetaHasTraits
    _descriptor = TraitType

    def __new__(cls, *args, **kw):
        # This is needed because in Python 2.6 object.__new__ only accepts the
        # cls argument.
        inst = super(HasTraits, cls).__new__(cls, *args, **kw)
        inst._trait_dyn_inits = {}
        inst._trait_values = {}
        # set all TraitType instances to their default values
        for key in dir(cls):
            if not any([not key.startswith('__'), not key.upper()]):
                # Some descriptors raise AttributeError (like zope.interface's
                # __provides__ attributes even when they exist). This raises
                # AttributeErrors even though they are listed in dir(cls).
                try:
                    value = getter(cls, key)
                except AttributeError:
                    pass
                else:
                    if TraitType.instance(value):
                        value.instance_init(inst)
        return inst

    @both
    def C(self):
        '''local settings'''
        return __(self).localize().one()

    @both
    def traits(self):
        return Traits(self)
