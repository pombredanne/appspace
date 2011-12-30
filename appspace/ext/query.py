# -*- coding: utf-8 -*-
'''appspace extension query'''

from __future__ import absolute_import

from inspect import getmro
from collections import deque

from stuf import stuf
from stuf.utils import clsname, get_or_default, setter

from appspace.core import AAppspace
from appspace.decorators import NoDefaultSpecified
from appspace.utils import getcls, itermembers, modname
from appspace.error import NoAppError, ConfigurationError
from appspace.builders import Appspace, Manager, Patterns, patterns


class Query(deque):

    '''manager query'''

    def __init__(self, appspace, *args, **kw):
        '''
        @param manager: an manager
        '''
        try:
            self._appspace = appspace.A
            self._this = appspace
        except (AttributeError, NoAppError):
            if AAppspace.providedBy(appspace):
                self._appspace = appspace
                self._this = kw.pop('this', None)
            else:
                raise NoAppError('appspace not found')
        self.manager = self._appspace.manager
        self.settings = self._appspace.manager.settings
        deque.__init__(self, *args)

    def __call__(self, *args):
        return getcls(self)(self._appspace, *args, **dict(this=self._this))

    def _tail(self, this):
        '''
        clear and put one thing in queue

        @param this: the thing
        '''
        self.clear()
        # append to queue
        self.appendleft(this)
        return self

    def app(self, label, branch='', app=''):
        '''
        add or get application from appspace

        @param label: application label
        @param branch: branch label (default: '')
        @param app: new application (default: '')
        '''
        if app:
            if branch:
                manager = self.branch(branch).one().manager
            else:
                manager = self.manager
            manager.set(label, app)
            return self._tail(app)
        if branch:
            return self._tail(self._appspace[branch][label])
        return self._tail(self._appspace[label])

    def apply(self, label, branch='', *args, **kw):
        '''
        call application from appspace

        @param label: application label
        @param branch: branch label (default: '')
        '''
        return self._tail(self._appspace[branch][label](*args, **kw))

    @classmethod
    def appspace(cls, pattern, required=None, defaults=None, *args, **kw):
        '''
        build new appspace

        @param pattern: pattern configuration class or appspace label
        @param required: required settings
        @param defaults: default settings
        @param *args: tuple of module paths or component inclusions
        '''
        if issubclass(pattern, Patterns):
            return cls(pattern.build(required, defaults))
        elif isinstance(pattern, basestring) and args:
            return cls(Patterns.settings(
                patterns(pattern, *args, **kw), required, defaults,
            ))
        raise ConfigurationError('patterns not found')

    def branch(self, label):
        '''
        add or get branch appspace

        @param label: label of appspace
        '''
        try:
            return self._tail(self._appspace[label])
        except NoAppError:
            new_appspace = Appspace(Manager())
            self.manager.set(label, new_appspace)
            return self._tail(new_appspace)
        raise ConfigurationError('invalid branch configuration')

    def filter(self, that):
        '''
        filter object members by a class

        @param that: class to filter by
        '''
        test = lambda x: isinstance(x, that)
        self.extendleft(i for i in itermembers(self._this, test))
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
        key = self.key().one()
        local_settings = self.settings.local[key] = stuf(dict(
            (k, v) for k, v in itermembers(m) if not k.startswith('_')
        ) for m in metas)
        local_settings.update(kw)
        return self._tail(local_settings)

    def key(self):
        '''identifier for component'''
        return self._tail(
            '_'.join([modname(self._this), clsname(self._this)]).lower()
        )

    def one(self):
        '''fetch one result'''
        try:
            return self.popleft()
        except IndexError:
            return []

    first = one

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

    def setting(self, key, value=NoDefaultSpecified, default=None):
        '''
        change setting in application settings

        @param key: name of settings
        @param value: value in settings
        @param default: setting value (default: None)
        '''
        if value is not NoDefaultSpecified:
            self.settings.set(key, value)
            return self
        return self._tail(self.settings.get(key, default))


# shortcut
__ = Query
