# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''traits keys'''

from __future__ import absolute_import

from appspace.keys import AppspaceKey, Attribute


class ATraits(AppspaceKey):

    C = Attribute('local settings')
    traits = Attribute('traits handler')


class ATrait(AppspaceKey):

    '''trait property key'''

    name = Attribute('attribute name')
    this_class = Attribute('class pointer')

    def instance_init(value):
        '''initialize instance with instance'''
