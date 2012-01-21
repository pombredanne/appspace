# -*- coding: utf-8 -*-
'''traits queue'''

from __future__ import absolute_import

from inspect import getmro
from itertools import ifilter

from stuf import stuf
from stuf.utils import get_or_default, getcls, lazy

from appspace.composing import ComposerQueue

from .mixins import TraitsMixin


class TraitQueue(TraitsMixin, ComposerQueue):

    '''double trait queue'''

    @lazy
    def traiter(self):
        '''trait query to attach to other apps'''
        return TraitQueue(self.manager)

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
        self.outgoing.append(settings)
        return self
        

__all__ = ['TraitQueue']
