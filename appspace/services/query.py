# -*- coding: utf-8 -*-
'''services query'''

from __future__ import absolute_import

from functools import partial
from operator import attrgetter

from stuf.utils import get_or_default

from appspace.query import Q


class Query(Q):

    '''service query'''

    def _serve(self, app, this):
        metadata = get_or_default(app, 'metadata', False)
        if metadata:
            kw = {}
            get = getattr
            for k in metadata:
                try:
                    kw[k] = get(this, k)
                except AttributeError:
                    pass
            if kw:
                app = partial(app, **kw)
        return app

    def resolve(self, label, this):
        '''
        resolve service

        @param label: application label
        '''
        servers = this._servers
        serve = self._serve
        for server in servers:
            try:
                item = serve(attrgetter(server + '.' + label)(this), this)
                if item:
                    setattr(this, label, item)
                    return item
            except AttributeError:
                pass
        else:
            raise AttributeError(label)


S = Query
__all__ = ['S']
