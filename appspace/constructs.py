# -*- coding: utf-8 -*-
## pylint: disable-msg=w0702
'''appspace component constructs'''

from __future__ import absolute_import
from types import MethodType
from functools import partial, wraps

from appspace.util import deferred_import, object_name

def delegate(**fkw):
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

def instance_component(this, label, appspace_label=None, appspace=None):
    '''
    inject appspaced component as instance attribute
    
    @param label: component label
    @param appspace_label: branch appspace label (default: None)
    @param appspace: appspace (default: None)
    '''
    if appspace is None:
        appspace = deferred_import('appspace.builder.app')
    # get configuration attribute label
    this_name = object.__getattribute__(this, label)
    if appspace_label is not None:
        # get configuration appspace label if set
        comp = appspace[
            object.__getattribute__(this, appspace_label)
        ][this_name]
    else:
        comp = appspace[this_name]
    object.__setattr__(this, label, comp)
    return comp


class class_component(object):

    '''lazily set appspaced component as class attribute on first access'''

    def __init__(self, label, appspace_label=None, appspace=None):
        '''
        @param label: component label
        @param appspace_label: branch appspace label (default: None)
        @param appspace: appspace (default: None)
        '''
        if appspace is None:
            appspace = deferred_import('appspace.builder.app')
        # configuration attribute label on class
        self.label = label
        # configuration attribute label on class
        self.appspace_label = appspace_label
        self.appspace = appspace

    def __get__(self, instance, owner):
        # get configuration attribute label
        label = getattr(owner, self.label)
        if self.appspace_label is not None:
            # get configuration appspace label if set
            return self.appspace[getattr(owner, self.appspace_label)][label]
        # setting the attribute on the class does bad things. DO NOT ATTEMPT!
        return self.appspace[label]


class delegated(object):

    '''delegates attribute to injected appspaced components'''

    def __init__(self, method, appspace=None):
        '''
        @param label: component label
        @param appspace: appspace (default: None)
        '''
        if appspace is None:
            appspace = deferred_import('appspace.builder.app')
        self.appspace = appspace
        self.method = method
        try:
            self.__doc__ = method.__doc__
            self.__module__ = method.__module__
            self.__name__ = object_name(method)
        except:
            pass

    def __get__(self, instance, owner):
        label, appspace_label = self.method(instance)
        # get configuration attribute label
        label = getattr(owner, label)
        if appspace_label is not None:
            # get configuration appspace label if set
            return self.appspace[getattr(owner, appspace_label)][label]
        return self.appspace[label]


class Delegated(object):
    
    '''
    class where attributes and methods can be delegated to appspaced components
    '''
    
    # list of delegates
    _delegates = {}
    
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

    def reset(self):
        '''reset all combined attributes that may have fired already'''
        instdict = set(self.__dict__.keys())
        classdict = self.__class__.__dict__
        # To reset them, we simply remove them from the instance dict. At that
        # point, it's as if they had never been computed. On the next access,
        # the accessor function from the parent class will be called, simply
        # because that's how the python descriptor protocol works.
        for mname, mval in classdict.items():
            if mname in instdict and isinstance(mval, delegated):
                delattr(self, mname)