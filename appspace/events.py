# -*- coding: utf-8 -*-
## pylint: disable-msg=f0401,w0232
'''appspace events'''

from __future__ import absolute_import

from zope.interface import implements as appifies

from .keys import AppspaceKey, AApp


class AEventHandler(AApp):

    '''holds events'''


class AEvent(AppspaceKey):

    '''event key'''


class APostCall(AEvent):

    '''call after another call'''


class APreCall(AEvent):

    '''call before another call'''


class AFirstPriority(AEvent):

    priority = 1


class ASecondPriority(AEvent):

    priority = 2


class AThirdPriority(AEvent):

    priority = 3


class AFourthPriority(AEvent):

    priority = 4


class AFifthPriority(AEvent):

    priority = 5


class ASixthPriority(AEvent):

    priority = 6


class ASeventhPriority(AEvent):

    priority = 7


class AEighthPriority(AEvent):

    priority = 8


class ANinthPriority(AEvent):

    priority = 9


class EventHandler(object):

    appifies(AEventHandler)

    precall = APreCall
    postcall = APostCall
    first = AFirstPriority
    second = ASecondPriority
    third = AThirdPriority
    fourth = AFourthPriority
    fifth = AFifthPriority
    sixth = ASixthPriority
    seventh = ASeventhPriority
    eighth = AEighthPriority
    ninth = ANinthPriority
