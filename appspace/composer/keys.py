# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
# pylint: disable-msg=f0401,e0213,e0211
'''extension keys'''

from __future__ import absolute_import

from inspect import ismodule

from appspace.keys import AppspaceKey
        

class AComposed(AppspaceKey):
    
    '''host key'''


class ASynched(AppspaceKey):
    
    '''synced key'''


__all__ = sorted(name for name, obj in locals().iteritems() if not any([
    name.startswith('_'), ismodule(obj),
]))

del ismodule
