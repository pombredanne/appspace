# -*- coding: utf-8 -*-
'''services queue'''

from __future__ import absolute_import

from functools import partial
from operator import attrgetter

from stuf.utils import get_or_default

from appspace.query import Queue


class ServicesQueue(Queue):

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
                    with self.sync():
                        setattr(this, label, item)
                        self.outappend(item)
                    break
            except AttributeError:
                pass
        return self


__all__ = ['Services']
