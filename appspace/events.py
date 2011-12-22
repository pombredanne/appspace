# -*- coding: utf-8 -*-
## pylint: disable-msg=f0401
'''appspace keys'''

from __future__ import absolute_import

from zope.interface import implements as appifies

from .keys import AEvent


class Event(object):

    appifies(AEvent)

    priority = 5


class PreCall(Event):
    pass


class PostCall(Event):
    pass


class FirstPriority(Event):

    priority = 1


class SecondPriority(Event):

    priority = 2


class ThirdPriority(Event):

    priority = 3


class FourthPriority(Event):

    priority = 4


class FifthPriority(Event):

    priority = 5


class SixthPriority(Event):

    priority = 6


class SeventhPriority(Event):

    priority = 7


class EighthPriority(Event):

    priority = 8


class NinthPriority(Event):

    priority = 9
