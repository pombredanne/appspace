# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''appspace extension service management'''

from functools import partial, wraps

from stuf.utils import getter, get_or_default

from appspace.keys import appifies
from appspace.error import NoAppError
from appspace.builders import Appspace
from appspace.registry import Registry

from .core import Builder, direct, factory
from .keys import AServiceManager, AService, AServer


def service(*metadata):
    '''
    marks method as service

    @param *metadata: metadata to set on decorated method
    '''
    def wrapped(this):
        this.metadata = metadata
        S.key(AService, this)
        @wraps(this) #@IgnorePep8
        def wrapper(*args, **kw):
            return this(*args, **kw)
        return wrapper
    return wrapped


class ServiceMixin(object):

    def __get__(self, this, that):
        new_app = super(ServiceMixin, self).__get__(this, that)
        S(new_app).scan(this, self.label)
        return new_app


class forward(ServiceMixin, factory):

    '''builds application in appspace and forwards host functionality to it'''

    appifies(AServer)


class remote(ServiceMixin, direct):

    '''makes remote functionality directly available to client'''


class servicer(factory):

    '''builds service and makes it available to clients'''

    def __get__(self, this, that):
        new_app = super(servicer, self).__get__(this, that)
        S.key(AService, new_app)
        return new_app


class ServiceManager(Registry):

    '''service manager'''

    __slots__ = ('_key', '_settings')

    appifies(AServiceManager)

    def __init__(self, ns='default'):
        '''
        init

        @param ns: label for internal namespace
        '''
        super(ServiceManager, self).__init__(AService, ns)


class ServiceQuery(Builder):

    '''service query'''

    def __init__(self, appspace, *args, **kw):
        '''
        init

        @param appspace: appspace or appspace server
        '''
        Builder.__init__(self, appspace, *args, **kw)
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

    def discover(self):
        '''
        register services

        @param client: client needing services
        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self(i for i in self.members(lambda x: self.keyed(AServer, x)))

    def fetch(self, label):
        '''
        fetch a service

        @param label: application label
        '''
        services = self._this._services
        # discover services
        if not services:
            self.discover()
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

    def scan(self, client, label):
        '''
        register services

        @param client: client needing services
        @param label: application label
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
            kw = {}
            client = self._this
            for k in metadata:
                if hasattr(client, k):
                    v = getter(client, k)
                    if v is not None:
                        kw[k] = v
            if kw:
                app = partial(app, **kw)
        self.appendleft(app)
        return self


S = ServiceQuery

__all__ = ('ServiceQuery', 'S', 'service')
