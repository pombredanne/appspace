# -*- coding: utf-8 -*-
'''query context managers'''
from appspace.ext.context import ContextManager


class AppContext(ContextManager):

    def __init__(self, queue, label, branch=False):
        '''
        init

        @param queue: query queue
        @param label: app label
        @param branch: branch label (default: False)
        '''
        def fallback():
            queue.clear_outgoing()
        super(AppContext, self).__init__(None, fallback)
        self.get = self.queue._qget
        self.label = label
        self.branch = branch
        self.app = None

    def __call__(self, label, branch=False, *args, **kw):
        return self.app(*args, **kw)

    def __enter__(self):
        self.app = self._qget(self.label, self.branch)

    def __exit__(self, type_, value, traceback):
        try:
            super(AppContext, self).__exit__(type_, value, traceback)
        except:
            raise
        self.queue.clear_incoming()
        self.queue.incoming.extend(self.queue.outgoing)
