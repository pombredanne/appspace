# -*- coding: utf-8 -*-
## pylint: disable-msg=w0702
'''appspace component constructs'''

from __future__ import absolute_import
from types import MethodType
from functools import partial, wraps

from appspace.util import ResetMixin, lazy_import, setter, getter


def appspacer(appspace):
    Appspaced.appspace = appspace
    return Appspaced


def delegater(appspace):
    Delegated.appspace = appspace
    return Appspaced


def delegatable(**fkw):
    '''
    delegated method marking decorator

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

    def __init__(self, setting, appspace_label):
        '''
        @param label: component label
        @param appspace: appspace (default: None)
        '''
        self.setting = setting

    def __get__(self, instance, owner):
        appspace = getter(instance, 'appspace', getter(owner, 'appspace'))
        if appspace is None:
            appspace = instance.appspace = lazy_import(
                'appspace.builder.app'
            )
        # get configuration attribute label
        if self.appspace_label is not None:
            # get configuration appspace label if set
            comp = appspace[self.appspace_label][self.label]
        else:
            comp = appspace[self.label]
        setter(owner, self.label, component)
        return component

    def _get_appspace(self, instance, owner):
        appspace = getter(instance, 'appspace', getter(owner, 'appspace'))
        if appspace is None:
            appspace = instance.appspace = lazy_import('appspace.builder.app')
        return appspace


class delegate(object):

    '''delegates attribute to appspaced components'''

    def __init__(self, setting):
        '''
        @param setting: setting
        '''
        self.setting = setting

    def __get__(self, instance, owner):
        appspace = getter(instance, 'appspace', getter(owner, 'appspace'))
        if appspace is None:
            appspace = instance.appspace = lazy_import(
                'appspace.builder.app'
            )
        # get configuration attribute label
        if self.appspace_label is not None:
            # get configuration appspace label if set
            return appspace[self.appspace_label][self.label]
        return appspace[self.label]


class Appspaced(ResetMixin):

    appspace = None
    _descriptor_class = component

    def _instance_component(self, label, appspace_label=None):
        '''
        inject appspaced component as instance attribute

        @param label: component label
        @param appspace_label: branch appspace label (default: None)
        @param appspace: appspace (default: None)
        '''
        if self.appspace is None:
            appspace = self.appspace = lazy_import('appspace.builder.app')
        # get configuration attribute label
        if appspace_label is not None:
            # get configuration appspace label if set
            comp = appspace[appspace_label][label]
        else:
            comp = appspace[label]
        setter(self, label, comp)
        return comp


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
            for component in self.__dict__.itervalues():
                if getattr(component, 'delegatable', False):
                    try:
                        this = object.__getattribute__(component, key)
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
