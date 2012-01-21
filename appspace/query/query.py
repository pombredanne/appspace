# -*- coding: utf-8 -*-
'''application query'''

from __future__ import absolute_import

from threading import local
from collections import Mapping, Sequence
from operator import attrgetter, itemgetter

from stuf.utils import lazy

from appspace.keys import AManager
from appspace.error import NoAppError


class Query(local):

    '''application query'''

    def __init__(self, appspace, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        super(Query, self).__init__()
        try:
            # fetch appspace from class
            self.manager = appspace.A
            # save the host class
            self._this = appspace
        except (AttributeError, NoAppError):
            # standalone appspace
            if AManager.providedBy(appspace):
                self.manager = appspace
                self._this = kw.pop('this', None)
            else:
                raise NoAppError('no appspace found')
        # appspace getter
        self._getter = self.manager.get

    @lazy
    def querier(self):
        '''query to attach to other apps'''
        return Query(self.manager)

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self.get(label, branch)(*args, **kw)

    _quikapply = apply

    def get(self, label, branch=False):
        '''
        get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self._getter(
            branch
        ).get(label) if branch else self._getter(label)

    _quikget = get

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        return self._getter(label)

    _quickbranch = branch

    @staticmethod
    def iskey(key):
        '''validate key'''
        return all([not key.startswith('_'), not key.isupper()])

    @staticmethod
    def itermembers(this):
        '''
        iterate over object members

        @param this: an object
        '''
        for key in dir(this):
            if not any([key.startswith('__'), key.isupper()]):
                try:
                    value = getattr(this, key)
                except AttributeError:
                    pass
                else:
                    yield key, value

    @classmethod
    def keyed(cls, key, this):
        '''
        check if item provides an app key

        @param label: app key
        @param this: object to check
        '''
        return cls.keyer(key, this[1])

    @staticmethod
    def keyer(key, this):
        '''
        check if item provides an app key

        @param label: app key
        @param this: object to check
        '''
        try:
            return key.providedBy(this)
        except (AttributeError, TypeError):
            try:
                return key.implementedBy(this)
            except (AttributeError, TypeError):
                return False

    def query(self, app):
        '''
        add query to app

        @param app: app to add query to
        '''
        app._Q = self.querier

    @staticmethod
    def plucker(key, data):
        '''
        fetch item from data structure by key

        @param key: label of item
        @param data: data containing item
        '''
        return itemgetter(key) if isinstance(
            data, (Mapping, Sequence)
        ) else attrgetter(key)


__all__ = ['Query']
