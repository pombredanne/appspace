# -*- coding: utf-8 -*-
'''building decorators'''

from __future__ import absolute_import

from inspect import isclass

from appspace.query import direct


class factory(direct):

    '''builds application stored in appspace and passes it to host'''

    def __init__(self, label, branch=False, *args, **kw):
        '''
        init

        @param label: application label
        @param branch: branch label (default: False)
        '''
        super(factory, self).__init__(label, branch)
        self.attrs = args
        self.extra = kw

    def __get__(self, this, that):
        new_app = super(factory, self).__get__(this, that)
        if isclass(new_app):
            attrs = [getattr(this, attr) for attr in self.attrs]
            new_app = new_app(*attrs, **self.extra)
            that._B.set(new_app, self.label, self.branch)
        return new_app


__all__ = ['factory']
