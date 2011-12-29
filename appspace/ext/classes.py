# -*- coding: utf-8 -*-
'''appspace classes'''

from __future__ import absolute_import

from inspect import isclass

from stuf.utils import either, setter, lazy

from .traits import Traits
from appspace.utils import getcls
from .containers import ResetMixin, Sync
from appspace.decorators import TraitType
from appspace.core import AHosted, appifies
from .query import __, component, delegated


class Hosted(ResetMixin):

    '''attributes and methods can be delegated to appspaced components'''

    appifies(AHosted)

    _descriptor = component

    def __new__(cls, *args, **kw):
        # needed because Python 2.6 object.__new__ only accepts cls argument
        __(cls).ons()
        new = super(Hosted, cls).__new__
        if new == object.__new__:
            return new(cls)
        return new(cls, *args, **kw)

    @either
    def c(self):
        '''local appspaced settings'''
        return self.q.localize().one()

    @either
    def q(self):
        return __(self)

    def _instance_component(self, name, label, branch=''):
        '''
        inject appspaced component as instance attribute

        @param name: instance attribute label
        @param label: component label
        @param branch: component branch (default: None)
        '''
        return setter(getcls(self), name, self.q.app(label, branch).one())


class Delegated(Hosted):

    '''attributes and methods can be delegated to appspaced components'''

    _delegated = {}
    _descriptor = delegated

    def __new__(cls, *args, **kw):
        # needed because Python 2.6 object.__new__ only accepts cls argument
        cls.q.delegated()
        return super(Delegated, cls).__new__(cls, *args, **kw)

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            func = self.q
            nkey = func.key()
            if key in self.s.delegates[nkey]:
                return func.app(key, nkey)


class Synched(Hosted):

    '''delegate with synchronized class'''

    def __init__(self, original, **kw):
        super(Synched, self).__init__()
        self._sync = Sync(original, **kw)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))


class MetaHasTraits(type):

    '''
    metaclass for HasTraits.

    This metaclass makes sure TraitType class attributes are instantiated with
    their name attribute set.
    '''

    def __new__(cls, name, bases, classdict):
        '''
        instantiate TraitTypes in classdict, setting their name attribute
        '''
        for k, v in classdict.iteritems():
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
        finish initializing HasTraits class

        This sets this_class attribute of each TraitType in the classdict to a
        newly created class.
        '''
        for v in classdict.itervalues():
            if TraitType.instance(v):
                v.this_class = cls
        super(MetaHasTraits, cls).__init__(name, bases, classdict)


class HasTraits(Synched):

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
            # Some descriptors raise AttributeError (like zope.interface's
            # __provides__ attributes even when they exist). This raises
            # AttributeErrors even though they are listed in dir(cls).
            try:
                value = getattr(cls, key)
            except AttributeError:
                pass
            else:
                if TraitType.instance(value):
                    value.instance_init(inst)
        return inst

    @lazy
    def traits(self):
        return Traits(self)
