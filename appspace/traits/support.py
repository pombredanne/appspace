# -*- coding: utf-8 -*-
'''trait support classes'''

from __future__ import absolute_import

from stuf.utils import deleter, lazy, lazybase


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


class ResetMixin(object):

    '''
    mixin to add a ".reset()" method to methods decorated with "lazybase"

    By default, lazy attributes, once computed, are static. If they happen to
    depend on other parts of an object and those parts change, their values may
    be out of sync.

    This class offers a ".reset()" method that an instance can call its state
    has changed and invalidate all their lazy attributes. Once reset() is
    called, all lazy attributes are reset to original format and their accessor
    functions can be triggered again.
    '''

    _descriptor_class = lazybase

    def reset(self):
        '''reset accessed lazy attributes'''
        instdict = vars(self)
        classdict = vars(self.__class__)
        desc = self._descriptor_class
        # To reset them, we simply remove them from the instance dict. At that
        # point, it's as if they had never been computed. On the next access,
        # the accessor function from the parent class will be called, simply
        # because that's how the python descriptor protocol works.
        for key, value in classdict.iteritems():
            if all([key in instdict, isinstance(value, desc)]):
                deleter(self, key)


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
    def all(self):
        return dict((k, v) for k, v in self.current.iteritems())

    @lazy
    def private(self):
        return dict(
            (k, v) for k, v in self.current.iteritems() if k.startswith('_')
        )

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
