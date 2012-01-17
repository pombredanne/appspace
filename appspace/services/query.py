# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''services query'''

from __future__ import absolute_import

from appspace.keys import appifies
from appspace.registry import Registry

from functools import partial

from stuf.utils import get_or_default

from appspace.query import B
from appspace.error import NoAppError
from appspace.builders import Appspace


from .keys import AServiceManager, AService, AServer


@appifies(AServiceManager)
class ServiceManager(Registry):

    '''service manager'''

    __slots__ = ('_key', '_settings')

    def __init__(self, ns='default'):
        '''
        init

        @param ns: label for internal namespace
        '''
        super(ServiceManager, self).__init__(AService, ns)


class ServiceQuery(B):

    '''service query'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        B.__init__(self, appspace, *args, **kw)
        # get existing service manager...
        self._appspace = self._manager.easy_lookup(
            AServiceManager, 'services',
        )
        # ... or initialize new service manager
        if self._appspace is None:
            self._appspace = self._manage_class
            self._manager.easy_register(
                AServiceManager, 'services', self._appspace
            )
        self._manager = self._appspace.manager

    @property
    def _manage_class(self):
        return Appspace(ServiceManager())

    def fetch(self, label):
        '''
        fetch a service

        @param label: application label
        '''
        services = self._this._services
        # discover services
        query = self.service
        # search services for application
        for serv in services:
            try:
                value = query(label, serv).one()
                if value is not None:
                    return value
            except NoAppError:
                pass
        else:
            raise AttributeError('{label} not found'.format(label=label))

    @classmethod
    def isserver(cls, key, value):
        '''
        detect service

        @param key: Trait name
        @param value: Trait value
        '''
        return all([cls.keyer(AServer, value), cls.iskey(key)])

    def scan(self, client, label):
        '''
        register services

        @param client: client needing services
        @param label: application label
        '''
        sget = self.get
        sset = self.set
        keyed = self.keyed
        check = lambda x: keyed(AService, x)
        for k, v in self.members(check):
            try:
                sget(k, label)
            except NoAppError:
                sset(k, label, v)
        client._services.add(label)
        return self

    def service(self, label, branch=False):
        '''
        add or get service from appspace

        @param label: application label
        @param branch: branch label (defalut: False)
        '''
        app = self._quikget(label, branch)
        metadata = get_or_default(app, 'metadata')
        get = getattr
        if metadata is not None:
            kw = {}
            client = self._this
            for k in metadata:
                if hasattr(client, k):
                    v = get(client, k)
                    if v is not None:
                        kw[k] = v
            if kw:
                app = partial(app, **kw)
        self.appendleft(app)
        return self


S = ServiceQuery
__all__ = ['S']
