# -*- coding: utf-8 -*-
'''traits support classes'''

from stuf.utils import lazy

from appspace.utils import ResetMixin


class _SimpleTest:

    def __init__(self, value):
        self.value = value

    def __call__(self, test):
        return test == self.value

    def __repr__(self):
        return '<SimpleTest(%r)' % self.value

    def __str__(self):
        return self.__repr__()


class Meta(object):

    def __new__(cls, **kw):
        for k, v in kw.iteritems():
            setattr(cls, k, v)
        return super(Meta, cls).__new__(cls)

    def __repr__(self):
        return 'Meta: %s' % str(dict((k, v) for k, v in vars(
            self.__class__
        ).iteritems() if not k.startswith('_')))


class Sync(ResetMixin):

    def __init__(self, original=None, **kw):
        super(Sync, self).__init__()
        self.original = original if original is not None else {}
        self.current = original.copy() if original else {}
        self.cleaned = {}
        if kw:
            self.changed = kw
            self.current.update(self.changed)
            self.modified = True
        else:
            self.changed = {}
            self.modified = False

    def __call__(self):
        return self.cleaned

    def __contains__(self, key):
        return key in self.current

    def __iter__(self):
        for k, v in self.current.iteritems():
            yield k, v

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(dict(i for i in self.current.iteritems()))

    __str__ = __unicode__

    @lazy
    def private(self):
        return dict(
            (k, v) for k, v in self.current.iteritems() if k.startswith('_')
        )

    @lazy
    def all(self):
        return dict((k, v) for k, v in self.current.iteritems())

    @lazy
    def public(self):
        return dict(
            (k, v) for k, v in self.current.iteritems()
            if not k.startswith('_')
        )

    def commit(self):
        self.modified = False
        self.update_original(self.current)
        self.cleaned.update(self.current.copy())
        self.changed.clear()

    def copy(self, **kw):
        previous = dict(i for i in self)
        previous.update(kw)
        return previous

    def rollback(self):
        self.changed.clear()
        self.reset()
        self.modified = False

    def reset(self):
        super(Sync, self).reset()
        self.current.clear()
        self.current.update(self.original.copy() if self.original else {})
        self.cleaned.clear()

    def update_current(self, kw):
        self.modified = True
        self.current.update(kw)
        self.changed.update(kw)
        self.cleaned.clear()

    def update_original(self, kw):
        self.original.update(kw)
        self.reset()
