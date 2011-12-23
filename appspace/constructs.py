# -*- coding: utf-8 -*-
'''constructs'''

from __future__ import absolute_import

from inspect import ismethod
from functools import partial, update_wrapper

from stuf.utils import (
    getter, get_or_default, instance_or_class, inverse_lookup, setter, selfname
)

from .utils import ResetMixin, lazy_import


def appspacer(appspace):
    '''
    add appspace to class

    @param appspace: appspace to add
    '''
    Appspaced.a = appspace
    Appspaced.s = appspace.appspace.settings
    return Appspaced


def delegater(appspace):
    '''
    add appspace to class

    @param appspace: appspace to add
    '''
    Delegated.a = appspace
    Delegated.s = appspace.appspace.settings
    return Delegated


def delegatable(**kw):
    '''
    marks method as being able to be delegated

    @param **fkw: attributes to set on decorated method
    '''
    def wrapped(func):
        return Delegatable(func, **kw)
    return wrapped


def get_appspace(this, owner):
    '''
    get the appspace attached to a class

    @param this: an instance
    @param owner: the instance's class
    '''
    appspace = instance_or_class('a', this, owner)
    if appspace is None:
        appspace = this.appspace = lazy_import('appspace.builder.app')
    return appspace


def get_component(appspace, label, branch=None):
    '''
    get component from appspace

    @param appspace: appspace
    @param label: component label
    @param branch: component branch (default: None)
    '''
    return appspace[branch][label] if branch is not None else appspace[label]


class component(object):

    '''lazily set appspaced component as class attribute on first access'''

    def __init__(self, label, branch=None):
        '''
        @param setting: a component setting
        '''
        self.label = label
        self.branch = branch

    def __get__(self, instance, owner):
        return get_component(
            get_appspace(instance, owner), self.label, self.branch,
        )


class delegate(component):

    '''delegates attribute to appspaced components'''


class Appspaced(ResetMixin):

    '''class with appspace attached'''

    _descriptor_class = component

    def _instance_component(self, name, label, branch=None):
        '''
        inject appspaced component as instance attribute

        @param name: instance attribute label
        @param label: component label
        @param branch: component branch (default: None)
        '''
        appspace = get_appspace(self, self.__class__)
        return setter(
            self,
            name,
            get_component(appspace, label, branch),
        )


class Delegated(Appspaced):

    '''attributes and methods can be delegated to appspaced components'''

    _delegates = {}
    _descriptor_class = delegatable
    a = None
    s = None

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            for comp in vars(self).itervalues():
                if get_or_default(comp, '_delegatable', False):
                    try:
                        this = getter(comp, key)
                        if ismethod(this):
                            pkwds = {}
                            for k, v in self._delegates:
                                if hasattr(this, k):
                                    pkwds[k] = getter(self, v)
                                this = partial(this, **pkwds)
                        setter(self.__class__, key, this)
                        return this
                    except AttributeError:
                        pass
            else:
                raise AttributeError('"{key}" not found'.format(key=key))


class Delegatable(object):

    delegated = True

    def __init__(self, method, **kw):
        self.method = method
        self.kw = kw
        self.name = selfname(method)
        update_wrapper(self, method)

    def __get__(self, this, that):
        method = self.method
        delegates = that._delegates
        if delegates:
            kw = dict(
                (k, getter(that, v)) for k, v in delegates.iteritems()
                if hasattr(that, k)
            )
            if kw:
                method = partial(method, **kw)
        return setter(that, self.name, method)
