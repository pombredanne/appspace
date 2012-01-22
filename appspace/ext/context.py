# -*- coding: utf-8 -*-
'''extensions context managers'''

from contextlib import GeneratorContextManager


class ContextManager(GeneratorContextManager):

    '''register callback to call in case of exception'''

    def __init__(self, gen, callback):
        super(ContextManager, self).__init__(gen)
        self.callback = callback

    def __exit__(self, type_, value, traceback):
        try:
            super(ContextManager, self).__exit__(type_, value, traceback)
        except:
            self.callback()
            raise
