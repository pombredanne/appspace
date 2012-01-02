# -*- coding: utf-8 -*-
'''appspace extension query'''

from __future__ import absolute_import

from inspect import getmro
from collections import deque
from itertools import groupby, ifilter, imap, ifilterfalse

from stuf import stuf
from stuf.utils import clsname, get_or_default, setter

from appspace.core import AAppspace, apped
from appspace.error import ConfigurationError, NoAppError
from appspace.utils import getcls, itermembers, modname, pluck
from appspace.builders import Appspace, Manager, Patterns, patterns

from .core import AServer, NoDefaultSpecified

__all__ = ['Query', '__']


class Query(deque):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: appspace or appspace host object
        '''
        try:
            # fetch appspace from class
            self._appspace = appspace.A
            # save the host class
            self._this = appspace
        except (AttributeError, NoAppError):
            # standalone appspace
            if AAppspace.providedBy(appspace):
                self._appspace = appspace
                self._this = kw.pop('this', None)
            else:
                raise NoAppError('appspace not found')
        # appspace manager
        self._manager = self._appspace.manager
        # appspace settings
        self._settings = self._appspace.manager.settings
        # appspace event manager
        self._events = self._appspace.manager.events
        # enable for traits
        self._enable = True
        deque.__init__(self, *args)

    def __call__(self, *args):
        return getcls(self)(self._appspace, *args, **dict(this=self._this))

    def _get(self, label, branch=False):
        return self.app(label, branch).one()

    def _tail(self, this):
        # clear queue
        self.clear()
        # append to queue
        self.append(this)
        return self

    def app(self, label, branch=False, app=False):
        '''
        add or get application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        @param app: new application (default: False)
        '''
        # process new application
        if app:
            # use branch manager
            if branch:
                manager = self.branch(branch).one().manager
            # use passed manager
            else:
                manager = self._manager
            # add to appspace
            manager.set(label, app)
            return self._tail(app)
        # return app from branch
        if branch:
            return self._tail(self._appspace[branch][label])
        # return from primary appsapce
        return self._tail(self._appspace[label])

    def apply(self, label, branch=False, *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self._tail(self._appspace[branch][label](*args, **kw))

    @classmethod
    def appspace(cls, pattern, required=None, defaults=None, *args, **kw):
        '''
        build new appspace

        @param pattern: pattern configuration class or appspace label
        @param required: required settings (default: None)
        @param defaults: default settings (default: None)
        @param *args: tuple of module paths or component inclusions
        '''
        # from appspace configuration class...
        if issubclass(pattern, Patterns):
            return cls(pattern.build(required, defaults))
        # from label and arguments...
        elif isinstance(pattern, basestring) and args:
            return cls(Patterns.settings(
                patterns(pattern, *args, **kw), required, defaults,
            ))
        raise ConfigurationError('patterns not found')

    def bind(self, event, label, branch=False):
        '''
        bind app to event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.bind(event, self._get(label, branch))
        return self

    def branch(self, label):
        '''
        add or fetch branch appspace

        @param label: label of appspace
        '''
        # fetch branch if exists...
        try:
            return self._tail(self._appspace[label])
        # create new branch
        except NoAppError:
            new_appspace = Appspace(Manager())
            self._manager.set(label, new_appspace)
            return self._tail(new_appspace)
        raise ConfigurationError('invalid branch configuration')

    def burst(self, label, queue):
        '''
        process event subscribers on contents of queue

        @param label: event label
        @param queue: queued arguments
        '''
        return self._tail(self._events.burst(label, queue))

    def defaults(self):
        '''default settings by their lonesome'''
        return self._tail(self._settings.defaults)

    def each(self, data, label, branch=False):
        '''
        run app in appsoace on each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self(app(i) for i in data)

    def event(self, label, priority=False, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: False)
        '''
        # unregister event
        if not priority or not kw:
            self._manager.unregister(label)
            return self
        # register event if priority and keywords passed
        return self._tail(self._manager.register(label, priority, **kw))

    def enable(self):
        '''toggle if trait events are allowed'''
        return self._tail(setter(self, '_enable', not self._enable))

    def find(self, data, label, branch=False):
        '''
        get first item in data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        for item in ifilter(app, data):
            return self._tail(item)

    def filter(self, data, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self(ifilter(app, data))

    def fire(self, event, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param event: event label
        '''
        return self._tail(self._events.fire(event, *args, **kw))

    def groupby(self, data, label, branch=False):
        '''
        group items from data by criteria of app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self(groupby(data, app))

    def id(self):
        '''identifier for component'''
        return self._tail(
            '_'.join([modname(self._this), clsname(self._this)]).lower()
        )

    def invoke(self, data, label, branch=False, *args, **kw):
        '''
        run app in appsoace on each item in data plus arbitrary args and
        keywords

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self(app(i, *args, **kw) for i in data)

    def key(self, key, app):
        apped(app, key)
        return self

    def last(self):
        '''fetch one last result'''
        try:
            return self.pop()
        except IndexError:
            return []

    def localize(self, **kw):
        '''
        generate local component settings

        **kw: settings to add to local settings
        '''
        this = self._this
        metas = [b.Meta for b in getmro(getcls(this)) if hasattr(b, 'Meta')]
        meta = get_or_default(this, 'Meta')
        if meta:
            metas.append(meta)
        local_settings = self._settings.local[self.id().one()] = stuf(dict(
            (k, v) for k, v in self.members(m, lambda x: not x.startswith('_'))
        ) for m in metas)
        local_settings.update(kw)
        return self._tail(local_settings)

    def map(self, data, label, branch=False):
        '''
        apply app in appspace to each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self(imap(app, data))

    def max(self, data, label, branch=False):
        '''
        find maximum by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self._tail(max(data, key=app))

    def members(self, test):
        '''
        fetch object members by class

        @param tester: test to filter by (default: False)
        '''
        return self(ifilter(test, itermembers(self._this)))

    def min(self, data, label, branch=False):
        '''
        find minimum value by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self._tail(min(data, key=app))

    def one(self):
        '''fetch one result'''
        try:
            return self.popleft()
        except IndexError:
            return []

    first = one
    
    def pluck(self, key, data):
        '''
        get items from data by key

        @param key: key to search for
        @param data: data to process
        '''
        return self(ifilter(
            lambda x: x is not None, (pluck(key, i) for i in data),
        ))

    def reduce(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = self._get(label, branch)
        return self._tail(reduce(app, data, initial))

    def register(self, model):
        '''
        register model in appspace

        @param model: class to be model
        '''
        # attach manager
        setter(model, 'A', self._appspace)
        # attach manager settings
        setter(model, 'S', self._settings.final)
        return self._tail(model)

    def reject(self, data, label, branch=False):
        '''
        fetch items from data for which app in appspace is false

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self(ifilterfalse(app, data))

    def required(self):
        '''required settings by their lonesome'''
        return self._tail(self._settings.required)

    def right_reduce(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace from right side

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        app = lambda x, y: self._get(label, branch)(y, x)
        return self._tail(reduce(app, reversed(data), initial))

    def setting(self, label, value=NoDefaultSpecified, default=None):
        '''
        change setting in application settings

        @param label: setting label
        @param value: value in settings (default: NoDefaultSpecified)
        @param default: setting value (default: None)
        '''
        if value is not NoDefaultSpecified:
            self._settings.set(label, value)
            return self
        return self._tail(self._settings.get(label, default))

    def sorted(self, data, label, branch=False):
        '''
        sort by key function in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        app = self._get(label, branch)
        return self(sorted(data, key=app))

    def spawn(self, appspace, *args, **kw):
        return getcls(self)(appspace, *args, **kw)

    def trigger(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        return self._tail(self._events.react(label))

    def unbind(self, event, label, branch=False):
        '''
        unbind app from event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self._events.unbind(event, self._get(label, branch))
        return self


__ = Query
