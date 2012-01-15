# -*- coding: utf-8 -*-
'''extension tests'''

from __future__ import absolute_import
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from appspace.error import NoAppError


class TestBuildFunctions(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from appspace.ext import __
        from appspace import patterns
        plug = patterns('helpers', ('get', 'math.sqrt'))
        __(plug).branch('branch').app('fabulous', 'branch', 'math.fabs')
        return plug

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.branch.fabulous, plug['branch']['fabulous'])
        self.assertEqual(plug.helpers.get, plug['helpers']['get'])

    def test_attr_multiple2(self):
        plug = self._make_multiple()
        self.assertRaises(
            NoAppError,
            lambda x: x == getattr(plug, 'make', ''),
            plug['branch']['fabulous'],
        )
        self.assertRaises(
            NoAppError,
            lambda x: x == getattr(plug.helpers, 'make', ''),
            plug['branch']['fabulous'],
        )
        self.assertRaises(
            NoAppError,
            lambda x: x == getattr(plug, 'make', ''),
            plug['helpers']['get'],
        )
        self.assertRaises(
            NoAppError,
            lambda x: x == getattr(plug.helpers, 'make', ''),
            plug['helpers']['get'],
        )

    def test_identity_namespace(self):
        from appspace.builders import Appspace
        plug = self._make_multiple()
        self.assertIsInstance(plug.helpers, Appspace)
        self.assertIsInstance(plug.branch, Appspace)

    def test_identity_multiple(self):
        from math import sqrt, fabs
        plug = self._make_multiple()
        self.assert_(plug.branch.fabulous is fabs)
        self.assert_(plug.helpers.get is sqrt)

    def test_call2_multiple(self):
        from math import sqrt, fabs
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.get(2), sqrt(2))
        self.assertEqual(plug.branch.fabulous(2), fabs(2))


if __name__ == '__main__':
    unittest.main()
