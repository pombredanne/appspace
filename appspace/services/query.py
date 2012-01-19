# -*- coding: utf-8 -*-
'''services query'''

from __future__ import absolute_import

from functools import partial
from operator import attrgetter

from stuf.utils import get_or_default

from appspace.query import Q


class Query(Q):

    '''service query'''

    def _serve(self, app):
        metadata = get_or_default(app, 'metadata', False)
        if metadata:
            kw = {}
            get = getattr
            this = self._this
            for k in metadata:
                try:
                    kw[k] = get(this, k)
                except AttributeError:
                    pass
            if kw:
                app = partial(app, **kw)
        return app

    def resolve(self, label):
        '''
        resolve service

        @param label: application label
        '''
        this = self._this
        servers = this._servers
        serve = self._serve
        for server in servers:
            try:
                item = serve(attrgetter(server + '.' + label)(this))
                if item:
                    setattr(self._this, label, item)
                    return item
            except AttributeError:
                pass
        else:
            raise AttributeError(label)


S = Query
__all__ = ['S']
