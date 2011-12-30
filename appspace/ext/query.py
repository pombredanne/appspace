# -*- coding: utf-8 -*-
'''appspace extension query'''

from __future__ import absolute_import

from collections import deque
from inspect import getmro, ismethod, isclass, isfunction
from itertools import ifilter, imap, groupby, ifilterfalse

from stuf import stuf
from stuf.utils import clsname, get_or_default, setter

from appspace.core import AAppspace
from appspace.decorators import NoDefaultSpecified
from appspace.error import ConfigurationError, NoAppError
from appspace.utils import getcls, isrelated, itermembers, modname
from appspace.builders import Appspace, Manager, Patterns, patterns


class Query(deque):

    '''appspace query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param appspace: a appspace or appspace host object
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
        # manager
        self.manager = self._appspace.manager
        # settings
        self.settings = self._appspace.manager.settings
        # enable for traits
        self._enable = True
        deque.__init__(self, *args)

    def __call__(self, *args):
        return getcls(self)(self._appspace, *args, **dict(this=self._this))

    def _tail(self, this):
        '''
        clear and put one thing in queue

        @param this: the thing
        '''
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
                manager = self.manager
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
        self.manager.events.bind(event, self.app(label, branch))
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
            self.manager.set(label, new_appspace)
            return self._tail(new_appspace)
        raise ConfigurationError('invalid branch configuration')

    def burst(self, label, queue):
        '''
        process event subscribers on contents of queue

        @param label: event label
        @param queue: queued arguments
        '''
        return self._tail(self.manager.events.burst(label, queue))

    def event(self, label, priority=False, **kw):
        '''
        create new event

        @param event: event label
        @param priority: priority of event (default: False)
        '''
        # unregister event
        if not priority or not kw:
            self.manager.unregister(label)
            return self
        # register event if priority and keywords passed
        return self._tail(self.manager.register(label, priority, **kw))

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
        for item in ifilter(self.app(label, branch).one(), data):
            return self._tail(item)

    def filter(self, data, label, branch=False):
        '''
        get items from data for which app in appspace is true

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self(i for i in ifilter(self.app(label, branch).one(), data))

    def fire(self, event, *args, **kw):
        '''
        fire event, passing in arbitrary positional arguments and keywords

        @param event: event label
        '''
        return self._tail(self.manager.events.fire(event, *args, **kw))

    def groupby(self, data, label, branch=False):
        '''
        group items from data by criteria of app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self(i for i in groupby(data, self.app(label, branch).one()))

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
        key = self.key().one()
        local_settings = self.settings.local[key] = stuf(dict(
            (k, v) for k, v in self.members(m, lambda x: not x.startswith('_'))
        ) for m in metas)
        local_settings.update(kw)
        return self._tail(local_settings)

    def key(self):
        '''identifier for component'''
        return self._tail(
            '_'.join([modname(self._this), clsname(self._this)]).lower()
        )

    def map(self, data, label, branch=False):
        '''
        apply app in appspace to each item in data

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self(i for i in imap(self.app(label, branch).one(), data))

    def members(self, tester=False):
        '''
        fetch object members by their class

        @param tester: test to filter by (default: False)
        '''
        if tester:
            if isclass(tester):
                test = lambda x: isrelated(x, tester)
            elif isfunction(tester):
                test = tester
        else:
            test = ismethod
        return self(
            i for i in ifilter(test, (i for i in itermembers(self._this)))
        )

    def one(self):
        '''fetch one result'''
        try:
            return self.popleft()
        except IndexError:
            return []

    first = one

    def reduce(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        return self._tail(reduce(self.app(label, branch).one(), data, initial))

    def register(self, model):
        '''
        register model in appspace

        @param model: class to be model
        '''
        # attach manager
        setter(model, 'A', self._appspace)
        # attach manager settings
        setter(model, 'S', self.settings)
        return self._tail(model)
    
    def reject(self, data, label, branch=False):
        '''
        fetch items from data for which app in appspace is false

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        '''
        return self(
            i for i in ifilterfalse(self.app(label, branch).one(), data)
        )
    
    def right_reduce(self, data, label, branch=False, initial=None):
        '''
        reduce data to single value with app in appspace from right side

        @param data: data to process
        @param label: application label
        @param branch: branch label (default: False)
        @param initial: initial value (default: None)
        '''
        return self._tail(reduce(
            lambda x, y: self.app(label, branch).one()(y, x), 
            reversed(data),
            initial,
        ))

    def setting(self, key, value=NoDefaultSpecified, default=None):
        '''
        change setting in application settings

        @param key: setting key
        @param value: value in settings (default: NoDefaultSpecified)
        @param default: setting value (default: None)
        '''
        if value is not NoDefaultSpecified:
            self.settings.set(key, value)
            return self
        return self._tail(self.settings.get(key, default))

    def trigger(self, label):
        '''
        returns objects bound to an event

        @param label: event label
        '''
        return self._tail(self.manager.events.react(label))

    def unbind(self, event, label, branch=False):
        '''
        unbind app from event

        @param event: event label
        @param label: application label
        @param branch: branch label (default: False)
        '''
        self.manager.events.unbind(event, self.app(label, branch).one())
        return self


# shortcut
__ = Query
