# -*- coding: utf-8 -*-
'''traits'''

from __future__ import absolute_import

from inspect import isclass, getmro

from stuf.utils import setter, get_or_default

from .utils import getcls, isrelated
from .collections import ResetMixin, Sync
from .decorators import TraitType, component, delegate, on


class Delegated(ResetMixin):

    '''attributes and methods can be delegated to appspaced components'''

    _descriptor_class = delegate
    _delegates = {}

    def __new__(cls, *args, **kw):
        # This is needed because in Python 2.6 object.__new__ only accepts the
        # cls argument.
        cls._metas = [b.Meta for b in getmro(cls) if hasattr(b, 'Meta')]
        return super(Delegated, cls).__new__(cls, *args, **kw)

    @classmethod
    def _c(cls):
        cls.s.update(dict(
            dict(
                (k, v) for k, v in vars(m).iteritems() if not k.startswith('_')
            ) for m in get_or_default(cls, '_metas', []) + [cls.Meta]
        ))

    def _instance_component(self, name, label, branch=None):
        '''
        inject appspaced component as instance attribute

        @param name: instance attribute label
        @param label: component label
        @param branch: component branch (default: None)
        '''
        setter(getcls(self), name, delegate(label, branch))


class Synched(Delegated):

    def __init__(self, original, **kw):
        '''
        set trait values using keyword arguments

        We need to use setattr for this to trigger validation and events.
        '''
        super(Synched, self).__init__()
        self._sync = Sync(original, **kw)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(dict(i for i in self._sync.public.iteritems()))


class MetaHasTraits(type):

    '''
    metaclass for HasTraits.

    This metaclass makes sure that any TraitType class attributes are
    instantiated and sets their name attribute.
    '''

    def __new__(cls, name, bases, classdict):
        '''
        instantiate all TraitTypes in class dict, setting their `name`
        attribute
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
        finish initializing HasTraits class.

        This sets the `this_class` attribute of each TraitType in the
        class dict to a newly created class.
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
