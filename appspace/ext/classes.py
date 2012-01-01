# -*- coding: utf-8 -*-
'''appspace classes'''

from __future__ import absolute_import

from inspect import isclass
from collections import deque
from itertools import chain, ifilter
from functools import partial, update_wrapper

from stuf.utils import getter, selfname, either, lazy, lazy_class, setter

from appspace.utils import getcls
from appspace.decorators import TraitType
from appspace.core import ADelegater, ADelegate, AHost, appifies

from .query import __
from .traits import Traits
from .containers import ResetMixin, Sync


__all__ = [
    'delegate', 'on', 'component', 'delegated', 'Delegate', 'Delegater',
    'HasTraits', 'Host', 'Synched'
]


def delegate(*metadata):
    '''
    marks method as delegate

    @param *metadata: metadata to set on decorated method
    '''
    def wrapped(func):
        return Delegatee(func, *metadata)
    return wrapped


def on(*events):
    '''
    marks method as being a lazy component

    @param *events: list of properties
    '''
    def wrapped(func):
        return On(func, *events)
    return wrapped


class component(object):

    '''attach appspaced component to class'''

    def __init__(self, label, branch=''):
        '''
        @param label: component label
        @param branch: component branch (default: '')
        '''
        self.label = label
        self.branch = branch
        self._appspace = False

    def __get__(self, this, that):
        return __(that).app(self.label, self.branch).one()

    def __set__(self, this, value):
        raise AttributeError('attribute is read only')

    def __delete__(self, this):
        raise AttributeError('attribute is read only')

    def __repr__(self, *args, **kwargs):
        return '{label}@{branch}'.format(label=self.label, branch=self.branch)


class delegated(component):

    '''delegated class functionality to component'''

    def __init__(self, label, branch='', *args):
        super(delegated, self).__init__(label, branch)
        self.args = args

    def __get__(self, this, that):
        '''
        get component from manager

        @param that: the instance's class
        '''
        app = super(delegated, self).__get__(this, that)
        __(that).key(ADelegater, app)
        return app(*[getter(this, arg) for arg in self.args])


class Base(ResetMixin):

    '''can have appspaced components attached'''

    _descriptor = component

    def __new__(cls, *args, **kw):
#        for _, v in cls.Q.members(On):
#            v.__get__(None, cls)
        new = super(Base, cls).__new__
        # needed because Python 2.6 object.__new__ only accepts cls argument
        if new == object.__new__:
            return new(cls)
        return new(cls, *args, **kw)

    @either
    def C(self):
        '''local appspaced settings'''
        return self.Q.localize().one()

    @either
    def Q(self):
        '''query instance'''
        return __(self)


class Methodology(object):

    def __init__(self, method, *metadata):
        self.method = method
        self.metadata = metadata
        update_wrapper(self, method)


class Delegatee(Methodology):

    '''method that can be delegated to another class'''

    def __get__(self, this, that):
        method = self.method
        if self.metadata:
            kw = dict(
                (k, getter(that, k)) for k in self.metadata if hasattr(this, k)
            )
            if kw:
                method = update_wrapper(partial(method, **kw), method)
        return method


class On(Methodology):

    '''attach events to method'''

    def __get__(self, this, that):
        ebind = __(that).manager.events.bind
        method = self.method
        for arg in self.events:
            ebind(arg, method)
        return setter(that, selfname(method), method)


class Host(Base):

    '''can have appspaced components attached'''

    appifies(AHost)


class Delegate(Base):

    '''can have attributes and methods delegated to it'''

    appifies(ADelegate)


class Delegater(Host):

    '''can delegate attributes and methods to appspaced components'''

    appifies(ADelegater)

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            try:
                value = self.Q.pluck(key, self.D).first()
                return setter(getcls(self), key, value)
            except KeyError:
                raise AttributeError('{0} not found'.format(key))

    @lazy_class
    def D(self):
        '''delegates'''
        Q = self.Q
        return deque(ifilter(
            lambda x: not isinstance(x, basestring),
            chain.from_iterable(Q.members(lambda x: Q.provides(ADelegate, x))),
        ))


class Synched(Host):

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
