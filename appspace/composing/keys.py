# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''extension keys'''

from __future__ import absolute_import

from inspect import ismodule

from appspace.keys import AppspaceKey
        

class AComposed(AppspaceKey):
    
    '''host key'''
    

class AComposedQueue(AComposed):
    
    '''host key'''


class ASynched(AComposed):
    
    '''synced key'''
    
    
class NoDefault(object):

    '''no default'''

    def generate(self, klass):
        '''generator'''


class Undefined(object):

    '''undefined value'''


NoDefault = NoDefault()
Undefined = Undefined()


__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
