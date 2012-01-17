# -*- coding: utf-8 -*-
'''composition utilities'''

from __future__ import absolute_import

from inspect import isclass

from stuf import stuf


def object_walk(this):
    '''
    transform classes within an object into stufs

    @param this: object
    '''
    this_stuf = stuf()
    for k, v in vars(this).iteritems():
        if not k.startswith('_'):
            if isclass(v):
                this_stuf[k] = object_walk(v)
            else:
                this_stuf[k] = v
    return this_stuf
