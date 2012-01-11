# -*- coding: utf-8 -*-
'''appspace traits classes'''

from __future__ import absolute_import

from inspect import isclass

from stuf.utils import both

from appspace.ext import Synced, __

from .api import Traits
from .core import TraitType
from .keys import ATraitType


class MetaHasTraits(type):

    '''
    metaclass to make sure TraitType class attributes are instantiated with
    their name attribute set.
    '''

    def __new__(cls, name, bases, classdict):
        '''
        new

        instantiate TraitTypes in classdict, setting their name attribute
        '''
        for k, v in classdict.iteritems():
            if all([__.keyer(ATraitType, v), __.iskey(k)]):
                if isclass(v):
                    vinst = v()
                    vinst.name = k
                    classdict[k] = vinst
                else:
                    v.name = k
        return super(MetaHasTraits, cls).__new__(cls, name, bases, classdict)

    def __init__(cls, name, bases, classdict):
        '''
        init

        finish initializing HasTraits class

        This sets this_class attribute of each TraitType in the classdict to a
        newly created class.
        '''
        classtraits = cls._classtraits
        for k, v in classdict.iteritems():
            if all([__.keyer(ATraitType, v), __.iskey(k)]):
                v.this_class = cls
                classtraits[k] = v
        super(MetaHasTraits, cls).__init__(name, bases, classdict)


class HasTraits(Synced):

    __metaclass__ = MetaHasTraits

    _descriptor = TraitType
    _classtraits = {}

    def __new__(cls, *args, **kw):
        inst = super(HasTraits, cls).__new__(cls, *args, **kw)
        inst._trait_dyn_inits = {}
        inst._trait_values = {}
        inst._traits = {}
        # set all TraitType instances to their default values
        for k, v in vars(cls).iteritems():
            if all([__.keyer(ATraitType, v), __.iskey(k)]):
                v.instance_init(inst)
                inst._traits[k] = v
        return inst

    @both
    def C(self):
        '''local settings'''
        return __(self).localize().one()

    @both
    def traits(self):
        '''traits handler'''
        return Traits(self)
