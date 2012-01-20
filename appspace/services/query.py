# -*- coding: utf-8 -*-
'''services query'''

from __future__ import absolute_import

from functools import partial
from operator import attrgetter

from stuf.utils import get_or_default  # , clsname

from appspace.query import Q


class Query(Q):

    '''service query'''

    def _serve(self, label, app, this):
        '''
        configure service

        @param app: application
        @param this: a client object
        '''
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
                # build app with new partial version with any keywords
                app = partial(app, **kw)
        self.manager.set('.'.join([this._key, label]), app)
        return app

    def resolve(self, label, this):
        '''
        resolve service

        @param label: application label
        @param this: a client object
        '''
        serve = self._serve
        for server in this._servers:
            try:
                item = serve(
                    label, attrgetter('.'.join([server, label]))(this), this,
                )
                if item:
                    setattr(this, label, item)
                    return item
            except AttributeError:
                pass


S = Query
__all__ = ['S']
