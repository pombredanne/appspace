# -*- coding: utf-8 -*-
# pylint: disable-msg=e0611
'''appspace tests'''

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from stuf.six import PY3

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
        self.assertIs(plug.get, sqrt)

    def test_call(self):
        from math import sqrt
        plug = self._make_one()
        self.assertEqual(plug('get', 2), sqrt(2))

    def test_call_multiple(self):
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
        self.assertEqual(plug.get, plug['get'])

    def test_attr_multiple2(self):
        plug = self._make_multiple()
        self.assertRaises(
            NoAppError,
            lambda x: x == getattr(plug, 'make', ''),
            plug['get'],
        )
        self.assertRaises(
            NoAppError,
            lambda x: x == getattr(plug, 'make', ''),
            plug['get'],
        )

    def test_identity_multiple(self):
        from math import sqrt
        plug = self._make_multiple()
        self.assertIs(plug.get, sqrt)

    def test_call_multiple(self):
        from math import sqrt
        plug = self._make_multiple()
        self.assertEqual(plug.get(2), sqrt(2))


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
        self.assertEqual(plug.square, plug['square'])
        self.assertEqual(plug.fabulous, plug['fabulous'])
        self.assertEqual(plug.formit, plug['formit'])
        self.assertEqual(plug.lower, plug['lower'])
        self.assertEqual(plug.upper, plug['upper'])
        self.assertEqual(plug.store, plug['store'])

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
        self.assert_(plug.square is sqrt)
        self.assert_(plug.fabulous is fabs)
        self.assert_(plug.formit is match)
        self.assert_(plug.lower is lowercase)
        self.assert_(plug.upper is uppercase)
        self.assert_(plug.store is UserDict)

    def test_call_multiple(self):
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
        self.assertEqual(plug.square(2), sqrt(2))
        self.assertEqual(plug.fabulous(2), fabs(2))
        self.assertEqual(
            plug.formit('2', '2').string, match('2', '2').string
        )
        self.assertEqual(plug.lower, lowercase)
        self.assertEqual(plug.upper, uppercase)
        self.assertEqual(plug.store, UserDict)


class TestAppconf(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from appspace import patterns, include
        app = patterns(
            'helpers', ('misc', include('appspace.tests.apps.appconf')),
        )
        return app

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.misc.square, plug['misc']['square'])
        self.assertEqual(plug.misc.fabulous, plug['misc']['fabulous'])
        self.assertEqual(plug.misc.formit, plug['misc']['formit'])
        self.assertEqual(plug.misc.mrk, plug['misc']['mrk'])
        self.assertEqual(plug.misc.furf, plug['misc']['furf'])
        self.assertEqual(plug.misc.mrnrf, plug['misc']['mrnrf'])

    def test_identity_multiple(self):
        from re import match
        from math import sqrt, fabs, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertIs(plug.misc.square, sqrt)
        self.assertIs(plug.misc.fabulous, fabs)
        self.assertIs(plug.misc.formit, match)
        self.assertIs(plug.misc.mrk, isinf)
        self.assertIs(plug.misc.furf, isnan)
        self.assertIs(plug.misc.mrnrf, exp)

    def test_call_multiple(self):
        from re import match
        from math import sqrt, fabs, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertEqual(plug.misc.square(2), sqrt(2))
        self.assertEqual(plug.misc.fabulous(2), fabs(2))
        self.assertEqual(
            plug.misc.formit('2', '2').string, match('2', '2').string
        )
        self.assertIs(plug.misc.mrk, isinf)
        self.assertIs(plug.misc.furf, isnan)
        self.assertIs(plug.misc.mrnrf, exp)


class TestPatterns(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from math import fabs
        from appspace import Patterns, class_patterns
        class helpers(Patterns): #@IgnorePep8
            square = 'math.sqrt'
            fabulous = fabs
            formit = 're.match'
            mrk = 'math.isinf'
            furf = 'math.isnan'
            mrnrf = 'math.exp'
        return class_patterns(helpers)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.square, plug['square'])
        self.assertEqual(plug.fabulous, plug['fabulous'])
        self.assertEqual(plug.formit, plug['formit'])
        self.assertEqual(plug.furf, plug['furf'])
        self.assertEqual(plug.mrk, plug['mrk'])
        self.assertEqual(plug.mrnrf, plug['mrnrf'])

    def test_identity_multiple(self):
        from re import match
        from math import sqrt, fabs, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertIs(plug.square, sqrt)
        self.assertIs(plug.fabulous, fabs)
        self.assertIs(plug.formit, match)
        self.assertIs(plug.mrk, isinf)
        self.assertIs(plug.furf, isnan)
        self.assertIs(plug.mrnrf, exp)

    def test_call_multiple(self):
        from re import match
        from math import sqrt, fabs, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertEqual(plug.square(2), sqrt(2))
        self.assertEqual(plug.fabulous(2), fabs(2))
        self.assertEqual(
            plug.formit('2', '2').string, match('2', '2').string
        )
        self.assertEqual(plug.mrk(2), isinf(2))
        self.assertEqual(plug.furf(2), isnan(2))
        self.assertEqual(plug.mrnrf(2), exp(2))


class TestNamespace(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from math import fabs
        from appspace import Patterns, Namespace, class_patterns
        class helpers(Patterns): #@IgnorePep8
            square = 'math.sqrt'
            fabulous = fabs
            formit = 'math.ceil'
            class subhelpers(Namespace): #@IgnorePep8
                mrk = 'math.isinf'
                furf = 'math.isnan'
                mrnrf = 'math.exp'
        return class_patterns(helpers)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.square, plug['square'])
        self.assertEqual(plug.fabulous, plug['fabulous'])
        self.assertEqual(plug.formit, plug['formit'])
        self.assertEqual(plug.subhelpers.furf, plug['subhelpers']['furf'])
        self.assertEqual(plug.subhelpers.mrk, plug['subhelpers']['mrk'])
        self.assertEqual(plug.subhelpers.mrnrf, plug['subhelpers']['mrnrf'])

    def test_identity_multiple(self):
        from math import sqrt, fabs, isinf, isnan, ceil, exp
        plug = self._make_multiple()
        self.assertIs(plug.square, sqrt)
        self.assertIs(plug.fabulous, fabs)
        self.assertIs(plug.formit, ceil)
        self.assertIs(plug.subhelpers.mrk, isinf)
        self.assertIs(plug.subhelpers.furf, isnan)
        self.assertIs(plug.subhelpers.mrnrf, exp)

    def test_call_multiple(self):
        from math import sqrt, fabs, ceil, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertEqual(plug.square(2), sqrt(2))
        self.assertEqual(plug.fabulous(2), fabs(2))
        self.assertEqual(plug.helpers.formit(2.6), ceil(2.6))
        self.assertEqual(plug.subhelpers.mrk(2), isinf(2))
        self.assertEqual(plug.subhelpers.furf(2), isnan(2))
        self.assertEqual(plug.subhelpers.mrnrf(2), exp(2))


class TestKeyedNamespace(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from math import fabs, exp
        from appspace.keys import AppspaceKey
        from appspace import Patterns, Namespace, class_patterns
        class TestKey(AppspaceKey): #@IgnorePep8
            '''test key'''
        class helpers(Patterns):
            square = 'math.sqrt'
            fabulous = fabs
            formit = 'math.ceil'
            class subhelpers(Namespace): #@IgnorePep8
                key = TestKey
                mrk = 'math.isinf'
                furf = 'math.isnan'
                mrnrf = exp
        return class_patterns(helpers)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.square, plug['square'])
        self.assertEqual(plug.fabulous, plug['fabulous'])
        self.assertEqual(plug.formit, plug['formit'])
        self.assertEqual(plug.subhelpers.furf, plug['subhelpers']['furf'])
        self.assertEqual(plug.subhelpers.mrk, plug['subhelpers']['mrk'])
        self.assertEqual(plug.subhelpers.mrnrf, plug['subhelpers']['mrnrf'])

    def test_identity_multiple(self):
        from math import sqrt, fabs, isinf, isnan, ceil, exp
        plug = self._make_multiple()
        self.assertIs(plug.square, sqrt)
        self.assertIs(plug.fabulous, fabs)
        self.assertIs(plug.formit, ceil)
        self.assertIs(plug.subhelpers.mrk, isinf)
        self.assertIs(plug.subhelpers.furf, isnan)
        self.assertIs(plug.subhelpers.mrnrf, exp)

    def test_call_multiple(self):
        from math import sqrt, fabs, ceil, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertEqual(plug.square(2), sqrt(2))
        self.assertEqual(plug.fabulous(2), fabs(2))
        self.assertEqual(plug.helpers.formit(2.6), ceil(2.6))
        self.assertEqual(plug.subhelpers.mrk(2), isinf(2))
        self.assertEqual(plug.subhelpers.furf(2), isnan(2))
        self.assertEqual(plug.subhelpers.mrnrf(2), exp(2))


class TestBranch(unittest.TestCase):

    @staticmethod
    def _make_multiple():
        from math import fabs
        from appspace import Patterns, Branch, class_patterns
        class helpers(Patterns): #@IgnorePep8
            square = 'math.sqrt'
            fabulous = fabs
            formit = 'math.ceil'
            class subhelpers(Branch): #@IgnorePep8
                misc = 'appspace.tests.apps.appconf'
        return class_patterns(helpers)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.misc.square, plug['misc']['square'])
        self.assertEqual(plug.misc.fabulous, plug['misc']['fabulous'])
        self.assertEqual(plug.misc.formit, plug['misc']['formit'])
        self.assertEqual(plug.misc.mrk, plug['misc']['mrk'])
        self.assertEqual(plug.misc.furf, plug['misc']['furf'])
        self.assertEqual(plug.misc.mrnrf, plug['misc']['mrnrf'])

    def test_identity_multiple(self):
        from re import match
        from math import sqrt, fabs, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertIs(plug.misc.square, sqrt)
        self.assertIs(plug.misc.fabulous, fabs)
        self.assertIs(plug.misc.formit, match)
        self.assertIs(plug.misc.mrk, isinf)
        self.assertIs(plug.misc.furf, isnan)
        self.assertIs(plug.misc.mrnrf, exp)

    def test_call_multiple(self):
        from re import match
        from math import sqrt, fabs, isinf, isnan, exp
        plug = self._make_multiple()
        self.assertEqual(plug.misc.square(2), sqrt(2))
        self.assertEqual(plug.misc.fabulous(2), fabs(2))
        self.assertEqual(
            plug.misc.formit('2', '2').string, match('2', '2').string
        )
        self.assertIs(plug.misc.mrk, isinf)
        self.assertIs(plug.misc.furf, isnan)
        self.assertIs(plug.misc.mrnrf, exp)

if __name__ == '__main__':
    unittest.main()
