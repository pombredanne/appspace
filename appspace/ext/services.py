# -*- coding: utf-8 -*-
# pylint: disable-msg=e1001,e1002
'''appspace extension service management'''

from itertools import chain, ifilter

from stuf import stuf

from appspace.keys import appifies
from appspace.builders import Appspace
from appspace.registry import Registry

from .query import Query
from .keys import AServiceManager, AService, AServer


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


class ServiceQuery(Query):

    def _manage_class(self):
        return Appspace(Services())

    def forwards(self):
        '''group forwarded apps together'''
        return self(
            ifilter(lambda x: not isinstance(x, str),
            chain(*self.members(lambda x: self.keyed(AServer, x)))),
        )

    def service(self, service, label, branch=False):
        pass

    def services(self, client, label, branch=False):
        '''
        register services

        @param client: client needing services
        @param label: application label
        @param branch: branch label (default: False)
        '''
        services = self.members(lambda x: self.keyed(AService, x))
        service_list = stuf({label: frozenset(i[0] for i in services)})
        if branch:
            self._settings.services[branch].update(service_list)
            client._services.add((label, branch))
        else:
            self._settings.services.update(service_list)
            client._services.add(label)
        self.appendleft(service_list)
        return self
