# -*- coding: utf-8 -*-
'''appspace tests'''

from __future__ import unicode_literals

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from six import PY3

if PY3:
    PATTERNS = (
        ('store', 'collections.UserDict'),
        ('lower', 'string.ascii_lowercase'),
        ('upper', 'string.ascii_uppercase'),
    )
else:
    PATTERNS = (
        ('store', 'UserDict.UserDict'),
        ('lower', 'string.lowercase'),
        ('upper', 'string.uppercase'),
    )

from appspace import NoAppError


class TestSingle(unittest.TestCase):

    @staticmethod
    def _make_one():
        from appspace import patterns
        return patterns('', ('get', 'math.sqrt'))

    def test_attr(self):
        plug = self._make_one()
        self.assertEqual(plug.get, plug['get'])

    def test_not_attr2(self):
        plug = self._make_one()
        self.assertNotEqual(
            NoAppError, lambda x: x == getattr(plug, 'foo', ''), plug['get'],
        )

    def test_identity(self):
        from math import sqrt
        plug = self._make_one()
        self.assert_(plug.get is sqrt)

    def test_call(self):
        from math import sqrt
        plug = self._make_one()
        self.assertEqual(plug('get', 2), sqrt(2))

    def test_call2(self):
        from math import sqrt
        plug = self._make_one()
        self.assertEqual(plug.get(2), sqrt(2))


class TestDouble(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from appspace import patterns
        return patterns('helpers', ('get', 'math.sqrt'))

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.get, plug['helpers']['get'])

    def test_attr_multiple2(self):
        plug = self._make_multiple()
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
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, Appspace)

    def test_identity_multiple(self):
        from math import sqrt
        plug = self._make_multiple()
        self.assert_(plug.helpers.get is sqrt)

    def test_call2_multiple(self):
        from math import sqrt
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.get(2), sqrt(2))


class TestQuintuple(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from math import fabs
        from appspace import patterns
        new_patterns = (
            ('square', 'math.sqrt'),
            ('fabulous', fabs),
            ('formit', 're.match'),
        ) + PATTERNS
        return patterns('helpers', *new_patterns)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.square, plug['helpers']['square'])
        self.assertEqual(plug.helpers.fabulous, plug['helpers']['fabulous'])
        self.assertEqual(plug.helpers.formit, plug['helpers']['formit'])
        self.assertEqual(plug.helpers.lower, plug['helpers']['lower'])
        self.assertEqual(plug.helpers.upper, plug['helpers']['upper'])
        self.assertEqual(plug.helpers.store, plug['helpers']['store'])

    def test_identity_namespace(self):
        from appspace.builders import Appspace
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, Appspace)

    def test_identity_multiple(self):
        from re import match
        from math import sqrt, fabs
        try:
            from UserDict import UserDict
            from string import lowercase, uppercase
        except ImportError:
            from collections import UserDict
            from string import (
                ascii_lowercase as lowercase, ascii_uppercase as uppercase
            )
        plug = self._make_multiple()
        self.assert_(plug.helpers.square is sqrt)
        self.assert_(plug.helpers.fabulous is fabs)
        self.assert_(plug.helpers.formit is match)
        self.assert_(plug.helpers.lower is lowercase)
        self.assert_(plug.helpers.upper is uppercase)
        self.assert_(plug.helpers.store is UserDict)

    def test_call2_multiple(self):
        from re import match
        from math import sqrt, fabs
        try:
            from UserDict import UserDict
            from string import lowercase, uppercase
        except ImportError:
            from collections import UserDict
            from string import (
                ascii_lowercase as lowercase, ascii_uppercase as uppercase
            )
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.square(2), sqrt(2))
        self.assertEqual(plug.helpers.fabulous(2), fabs(2))
        self.assertEqual(
            plug.helpers.formit('2', '2').string, match('2', '2').string
        )
        self.assertEqual(plug.helpers.lower, lowercase)
        self.assertEqual(plug.helpers.upper, uppercase)
        self.assertEqual(plug.helpers.store, UserDict)


class TestAppconf(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from appspace import patterns, include
        app = patterns(
            'helpers',
            ('misc', include('appspace.tests.apps')),
        )
        return app

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(
            plug.helpers.misc.square, plug['helpers']['misc']['square']
        )
        self.assertEqual(
            plug.helpers.misc.fabulous, plug['helpers']['misc']['fabulous']
        )
        self.assertEqual(
            plug.helpers.misc.formit, plug['helpers']['misc']['formit']
        )
        self.assertEqual(
            plug.helpers.misc.lower, plug['helpers']['misc']['lower']
        )
        self.assertEqual(
            plug.helpers.misc.upper, plug['helpers']['misc']['upper']
        )
        self.assertEqual(
            plug.helpers.misc.store, plug['helpers']['misc']['store']
        )

    def test_identity_namespace(self):
        from appspace.builders import Appspace
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, Appspace)

    def test_identity_multiple(self):
        from re import match
        from math import sqrt, fabs
        try:
            from UserDict import UserDict
            from string import lowercase, uppercase
        except ImportError:
            from collections import UserDict
            from string import (
                ascii_lowercase as lowercase, ascii_uppercase as uppercase
            )
        plug = self._make_multiple()
        self.assert_(plug.helpers.misc.square is sqrt)
        self.assert_(plug.helpers.misc.fabulous is fabs)
        self.assert_(plug.helpers.misc.formit is match)
        self.assert_(plug.helpers.misc.lower is lowercase)
        self.assert_(plug.helpers.misc.upper is uppercase)
        self.assert_(plug.helpers.misc.store is UserDict)

    def test_call2_multiple(self):
        from re import match
        from math import sqrt, fabs
        try:
            from UserDict import UserDict
            from string import lowercase, uppercase
        except ImportError:
            from collections import UserDict
            from string import (
                ascii_lowercase as lowercase, ascii_uppercase as uppercase
            )
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.misc.square(2), sqrt(2))
        self.assertEqual(plug.helpers.misc.fabulous(2), fabs(2))
        self.assertEqual(
            plug.helpers.misc.formit('2', '2').string, match('2', '2').string
        )
        self.assertEqual(plug.helpers.misc.lower, lowercase)
        self.assertEqual(plug.helpers.misc.upper, uppercase)
        self.assertEqual(plug.helpers.misc.store, UserDict)


class TestPatterns(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from math import fabs
        from appspace import Patterns, class_patterns
        class helpers(Patterns):
            square = 'math.sqrt'
            fabulous = fabs
            formit = 're.match'
            if PY3:
                lower = 'string.ascii_lowercase'
                upper = 'string.ascii_uppercase'
                store = 'collections.UserDict'
            else:
                lower = 'string.lowercase'
                upper = 'string.uppercase'
                store = 'UserDict.UserDict'
        return class_patterns('helpers', helpers)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.square, plug['helpers']['square'])
        self.assertEqual(plug.helpers.fabulous, plug['helpers']['fabulous'])
        self.assertEqual(plug.helpers.formit, plug['helpers']['formit'])
        self.assertEqual(plug.helpers.lower, plug['helpers']['lower'])
        self.assertEqual(plug.helpers.upper, plug['helpers']['upper'])
        self.assertEqual(plug.helpers.store, plug['helpers']['store'])

    def test_identity_namespace(self):
        from appspace.builders import Appspace
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, Appspace)

    def test_identity_multiple(self):
        from re import match
        from math import sqrt, fabs
        try:
            from UserDict import UserDict
            from string import lowercase, uppercase
        except ImportError:
            from collections import UserDict
            from string import (
                ascii_lowercase as lowercase, ascii_uppercase as uppercase
            )
        plug = self._make_multiple()
        self.assert_(plug.helpers.square is sqrt)
        self.assert_(plug.helpers.fabulous is fabs)
        self.assert_(plug.helpers.formit is match)
        self.assert_(plug.helpers.lower is lowercase)
        self.assert_(plug.helpers.upper is uppercase)
        self.assert_(plug.helpers.store is UserDict)

    def test_call2_multiple(self):
        from re import match
        from math import sqrt, fabs
        try:
            from UserDict import UserDict
            from string import lowercase, uppercase
        except ImportError:
            from collections import UserDict
            from string import (
                ascii_lowercase as lowercase, ascii_uppercase as uppercase
            )
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.square(2), sqrt(2))
        self.assertEqual(plug.helpers.fabulous(2), fabs(2))
        self.assertEqual(
            plug.helpers.formit('2', '2').string, match('2', '2').string
        )
        self.assertEqual(plug.helpers.lower, lowercase)
        self.assertEqual(plug.helpers.upper, uppercase)
        self.assertEqual(plug.helpers.store, UserDict)


if __name__ == '__main__':
    unittest.main()
