# -*- coding: utf-8 -*-
'''traits query'''

from __future__ import absolute_import

from inspect import getmro
from itertools import ifilter

from stuf import stuf
from stuf.utils import get_or_default, getcls, lazy

from appspace.compose import ComposerQuery

from .mixins import TraitsMixin


class TraitQuery(TraitsMixin, ComposerQuery):

    '''trait query'''

    @lazy
    def traiter(self):
        '''trait query to attach to other apps'''
        return TraitQuery(self.manager)

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
        return settings
        

T = TraitQuery
__all__ = ['TraitQuery']
