# -*- coding: utf-8 -*-
'''traits query'''

from __future__ import absolute_import

from itertools import ifilter
from types import FunctionType
from inspect import getargspec, getmro, ismethod

from stuf import stuf
from stuf.utils import get_or_default, getcls

from appspace.composer import __

from .keys import ATrait


class _SimpleTest:

    '''simple test'''

    def __init__(self, value):
        self.value = value

    def __call__(self, test):
        return test == self.value

    def __repr__(self):
        return '<SimpleTest(%r)' % self.value

    def __str__(self):
        return self.__repr__()


class TraitQuery(__):

    '''trait query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: appspace or appspace server
        '''
        __.__init__(self, appspace, *args, **kw)
        # enable for traits
        self._enabled = True

    @property
    def enabled(self):
        '''are trait events allowed'''
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        '''
        enable trait events

        @param value: True or False
        '''
        self._enabled = value

    @classmethod
    def istrait(cls, key, value):
        '''
        detect Trait

        @param key: Trait name
        @param value: Trait value
        '''
        return all([cls.keyer(ATrait, value), cls.iskey(key)])

    def localize(self, **kw):
        '''
        generate local component settings

        **kw: settings to add to local settings
        '''
        this = self._this
        metas = [b.Meta for b in getmro(getcls(this)) if hasattr(b, 'Meta')]
        meta = get_or_default(this, 'Meta')
        if meta:
            metas.append(meta)
        settings = stuf()
        for m in metas:
            for k, v in ifilter(
                lambda x: not x[0].startswith('_'), self.itermembers(m),
            ):
                settings[k] = v
        settings.update(kw)
        self.appendleft(settings)
        return self

    @staticmethod
    def traits(traits, **metadata):
        '''
        get a list of all the traits of this class

        @param traits: traits
        @param **metadata: metadata to filter by

        This method is a class method equivalent of the traits method.

        The traits returned know nothing about the values that Traits'
        instances are holding.

        This follows the same algorithm as traits does and does not allow for
        any simple way of specifying merely that a metadata name exists, but
        has any value.  This is because get_metadata returns None if a metadata
        key doesn't exist.
        '''
        if not metadata:
            return traits
        for meta_name, meta_eval in metadata.iteritems():
            if type(meta_eval) is not FunctionType:
                metadata[meta_name] = _SimpleTest(meta_eval)
        result = {}
        for name, trait in traits.iteritems():
            get_metadata = trait.get_metadata
            for meta_name, meta_eval in metadata.iteritems():
                if not meta_eval(get_metadata(meta_name)):
                    break
            else:
                result[name] = trait
        return result

    def fire(self, label, old_value, new_value, **kw):
        '''
        process trait related event

        @param label: trait event label
        @param old_value: old trait value
        @param new_value: new trait value
        '''
        if self.enabled:
            # First dynamic ones
            callables = self.react(label).one()
            # Call them all now
            for C in callables:
                # Traits catches and logs errors here. I allow them to raise.
                if callable(C):
                    argspec = getargspec(C)
                    nargs = len(argspec[0])
                    # Bound methods have an additional 'self' argument. I don't
                    # know how to treat unbound methods, but they can't really
                    # be used for callbacks.
                    if ismethod(C):
                        offset = -1
                    else:
                        offset = 0
                    if nargs + offset == 0:
                        C()
                    elif nargs + offset == 1:
                        C(label)
                    elif nargs + offset == 2:
                        C(label, new_value)
                    elif nargs + offset == 3:
                        C(label, old_value, new_value)
                    else:
                        raise TypeError(
                            'Trait callback must have 0-3 arguments'
                        )
                else:
                    raise TypeError('Trait callback must be callable')


T = TraitQuery
