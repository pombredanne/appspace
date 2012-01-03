# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''appspace extension service management'''

from functools import partial, wraps

from stuf.utils import getter

from appspace.keys import appifies
from appspace.builders import Appspace
from appspace.registry import Registry

from .core import Query
from .keys import AServiceManager, AService

__all__ = ['ServiceQuery', 'S', 'service']


def service(*metadata):
    '''
    marks method as service

    @param *metadata: metadata to set on decorated method
    '''
    def wrapped(this):
        this.metadata = metadata
        S.key(AService, this)

        @wraps(this)
        def wrapper(*args, **kw):
            return this(*args, **kw)
        return wrapper
    return wrapped


class Service(object):

    '''method that can be delegated to another class'''

    def __get__(self, this, that):
        method = self.method
        kw = {}
        if self.metadata:
            kw.update(dict(
                (k, getter(that, k)) for k in self.metadata if hasattr(this, k)
            ))
        new_method = partial(method, this, **kw)
        return new_method


class ServiceQuery(Query):

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: appspace or appspace server
        '''
        Query.__init__(self, appspace, *args, **kw)
        self._appmanager = self._manager
        self._appappspace = self._appspace
        # get existing service manager...
        self._appspace = self._appmanager.easy_lookup(
            AServiceManager, 'services',
        )
        # ... or initialize new service manager
        if self._appspace is None:
            self._appspace = self._manage_class
            self._appmanager.easy_register(
                AServiceManager, 'services', self._appspace
            )
        self._manager = self._appspace.manager

    @property
    def _manage_class(self):
        return Appspace(Services())

    def scan(self, client, label, branch=False):
        '''
        register services

        @param client: client needing services
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app
        for k, v in self.members(lambda x: self.keyed(AService, x)):
            app(k, label, v)
        if branch:
            client._services.add((label, branch))
        else:
            client._services.add((label, False))
        return self

    def service(self, app, label, branch=False):
        pass


class Services(Registry):

    '''service manager'''

    __slots__ = ['_key', '_settings']

    appifies(AServiceManager)

    def __init__(self, ns='default'):
        '''
        init

        @param ns: label for internal namespace
        '''
        super(Services, self).__init__(AService, ns)


S = ServiceQuery
