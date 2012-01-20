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
        label = self.label
        branch = self.branch
        new_app = that._Q.get(label, branch)
        if isclass(new_app):
            new_app = new_app(
                *[getattr(this, attr) for attr in self.attrs], **self.extra
            )
            that._B.set(new_app, label, branch)
        setattr(that, label, new_app)
        return new_app


__all__ = ['factory']
