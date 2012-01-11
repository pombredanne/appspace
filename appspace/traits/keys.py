# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''traits keys'''

from appspace.keys import AppspaceKey, Attribute


class ATraitType(AppspaceKey):

    '''trait property key'''

    name = Attribute('attribute name')
    this_class = Attribute('class pointer')

    def instance_init(this):
        '''initialize instance with instance'''


class ATraits(AppspaceKey):
    pass


class AHasTraits(AppspaceKey):
    
    
    C = Attribute('local settings')
    traits = Attribute('traits handler')
