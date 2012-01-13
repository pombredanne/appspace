# -*- coding: utf-8 -*-
'''trait query'''

from inspect import getmro
from itertools import ifilter

from stuf import stuf
from stuf.utils import get_or_default, getcls, setter

from appspace.ext import Sync
from appspace.ext.apps import AppQuery

from .keys import ATraitType


class TraitSync(Sync):

    '''trait sync'''

    def __init__(self, original, **kw):
        super(TraitSync, self).__init__(original, **kw)
        self._traits = stuf()
        self._trait_values = stuf()


class TraitQuery(AppQuery):

    '''trait query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: appspace or appspace server
        '''
        AppQuery.__init__(self, appspace, *args, **kw)
        # enable for traits
        self._enable = True

    def enable(self):
        '''toggle if trait events are allowed'''
        self.appendleft(setter(self, '_enable', not self._enable))
        return self

    @classmethod
    def istrait(cls, key, value):
        return cls.keyer(ATraitType, value) and cls.iskey(key)

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

    def trait(self, name, old_value, new_value):
        '''
        process trait related event

        @param label: trait event label
        @param old_value: old trait value
        @param new_value: new trait value
        '''
        self._events.trait(name, old_value, new_value)
        

T = TraitQuery