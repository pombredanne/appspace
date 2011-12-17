# -*- coding: utf-8 -*-
## pylint: disable-msg=e1103
'''appspace component constructs'''

from __future__ import absolute_import
from types import MethodType
from functools import partial, wraps

from stuf.utils import setter, instance_or_class, inverse_lookup, object_lookup

from .utils import ResetMixin, lazy_import


def appspacer(appspace):
    '''
    add appspace to class

    @param appspace: appspace to add
    '''
    Appspaced.appspace = appspace
    return Appspaced


def delegater(appspace):
    '''
    add appspace to class

    @param appspace: appspace to add
    '''
    Delegated.appspace = appspace
    return Appspaced


def get_appspace(this, owner):
    '''
    get the appspace attached to a class

    @param this: an instance
    @param owner: the instance's class
    '''
    appspace = instance_or_class('appspace', this, owner)
    if appspace is None:
        appspace = this.appspace = lazy_import('appspace.builder.app')
    return appspace


def delegatable(**fkw):
    '''
    marks method as being able to be delegated

    @param **fkw: attributes to set on decorated method
    '''
    def wrapped(func):
        func.delegated = True
        for k, v in fkw.iteritems():
            setattr(func, k, v)

        @wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        return wrapper
    return wrapped


class component(object):

    '''lazily set appspaced component as class attribute on first access'''

    def __init__(self, *setting):
        '''
        @param setting: a component setting
        '''
        self.setting = tuple(reversed(setting))

    def __get__(self, instance, owner):
        appspace = get_appspace(instance, owner)
        return setter(
            owner,
            inverse_lookup(self, owner),
            object_lookup(appspace.settings.lookup(self.setting), appspace),
        )


class delegate(component):

    '''delegates attribute to appspaced components'''


class Appspaced(ResetMixin):

    appspace = None
    _descriptor_class = component

    def _instance_component(self, label, *setting):
        '''
        inject appspaced component as instance attribute

        @param label: instance attribute label
        @param setting: a component setting
        '''
        appspace = get_appspace(self, self.__class__)
        return setter(
            self,
            label,
            object_lookup(appspace.settings.lookup(setting), appspace),
        )


class Delegated(Appspaced):

    '''
    class where attributes and methods can be delegated to appspaced components
    '''

    # list of delegates
    _delegates = {}
    _descriptor_class = delegatable

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            for comp in vars(self).itervalues():
                if getattr(comp, '_delegatable', False):
                    try:
                        this = object.__getattribute__(comp, key)
                        if isinstance(this, MethodType):
                            pkwds = {}
                            for k, v in self._delegates:
                                if hasattr(this, k):
                                    pkwds[k] = object.__getattribute__(self, v)
                                this = partial(this, **pkwds)
                        setattr(self.__class__, key, this)
                        return this
                    except AttributeError:
                        pass
            else:
                raise AttributeError('"{key}" not found'.format(key=key))
