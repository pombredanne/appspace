# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''appspace extension service management'''

from functools import partial, wraps

from stuf.utils import getter, get_or_default

from appspace.keys import appifies
from appspace.builders import Appspace
from appspace.registry import Registry

from .core import Query
from .keys import AServiceManager, AService
from appspace.ext.keys import AServer
from appspace.error import NoAppError


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


class ServiceQuery(Query):

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        Query.__init__(self, appspace, *args, **kw)
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
        return Appspace(Services())

    def discover(self):
        '''
        register services

        @param client: client needing services
        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self(i for i in self.members(lambda x: self.keyed(AServer, x)))

    def fetch(self, key):
        services = self._this._services
        if not services:
            self.discover()
        query = self.service
        for serv in services:
            try:
                value = query(key, serv)
                if value is not None:
                    return value
            except NoAppError:
                pass
#            else:
#                raise AttributeError('{0} not found'.format(key))

    def scan(self, client, label):
        '''
        register services

        @param client: client needing services
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self.app
        for k, v in self.members(lambda x: self.keyed(AService, x)):
            app(k, label, v)
        client._services.add(label)
        return self

    def service(self, label, branch):
        '''
        add or get service from appspace

        @param label: application label
        @param branch: branch label
        '''
        app = self.app(label, branch).first()
        metadata = get_or_default(app, 'metadata')
        if metadata is not None:
            client = self._this
            kw = {}
            for k in metadata:
                if hasattr(client, k):
                    kw[k] = getter(client, k)
            app = partial(app, **kw)
        self.appendleft(app)
        return self


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

__all__ = ['ServiceQuery', 'S', 'service']
