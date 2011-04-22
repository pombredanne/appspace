'''appspace tests'''

import unittest


class TestSingle(unittest.TestCase):

    def _make_one(self):
        from appspace.builder import AppspaceFactory, App
        return App(AppspaceFactory('', ('get', 'math.sqrt')).appspace)

    def test_init(self):
        plug = self._make_one()
        self.assertEqual('get' in plug, True)

    def test_attr(self):
        plug = self._make_one()
        self.assertEqual(plug.get, plug['get'])

    def test_not_init(self):
        plug = self._make_one()
        self.assertNotEqual('foo' in plug, True)

    def test_not_attr2(self):
        plug = self._make_one()
        self.assertNotEqual(getattr(plug, 'foo', ''), plug['get'])

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

    def _make_multiple(self):
        from appspace.builder import AppspaceFactory, App
        return App(AppspaceFactory('helpers', ('get', 'math.sqrt')).appspace)

    def test_init_multiple(self):
        plug = self._make_multiple()
        self.assertEqual('get' in plug['helpers'], True)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.get, plug['helpers']['get'])

    def test_init_multiple2(self):
        plug = self._make_multiple()
        self.assertNotEqual('foo' in plug['helpers'], True)
        self.assertNotEqual('foo' in plug, True)

    def test_attr_multiple2(self):
        plug = self._make_multiple()
        self.assertNotEqual(getattr(plug, 'make', ''), plug['helpers']['get'])
        self.assertNotEqual(
            getattr(plug.helpers, 'make', ''), plug['helpers']['get']
        )

    def test_identity_namespace(self):
        from appspace.builder import App
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, App)

    def test_identity_multiple(self):
        from math import sqrt
        plug = self._make_multiple()
        self.assert_(plug.helpers.get is sqrt)

    def test_call_multiple(self):
        from math import sqrt
        plug = self._make_multiple()
        self.assertEqual(plug(('helpers', 'get'), 2), sqrt(2))

    def test_call2_multiple(self):
        from math import sqrt
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.get(2), sqrt(2))


class TestTriple(unittest.TestCase):

    def _make_multiple(self):
        from math import fabs
        from appspace.builder import AppspaceFactory, App
        return App(AppspaceFactory(
            ('helpers', 'math'),
            ('sqrt', 'math.sqrt'),
            ('fabs', fabs),
        ).appspace)

    def test_init_multiple(self):
        plug = self._make_multiple()
        self.assertEqual('sqrt' in plug['helpers']['math'], True)
        self.assertEqual('fabs' in plug['helpers']['math'], True)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(
            plug.helpers.math.sqrt, plug['helpers']['math']['sqrt']
        )
        self.assertEqual(
            plug.helpers.math.fabs, plug['helpers']['math']['fabs']
        )

    def test_identity_namespace(self):
        from appspace.builder import App
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, App)
        self.assertIsInstance(app.helpers.math, App)

    def test_identity_multiple(self):
        from math import sqrt, fabs
        plug = self._make_multiple()
        self.assert_(plug.helpers.math.sqrt is sqrt)
        self.assert_(plug.helpers.math.fabs is fabs)

    def test_call_multiple(self):
        from math import sqrt, fabs
        plug = self._make_multiple()
        self.assertEqual(plug(('helpers', 'math', 'sqrt'), 2), sqrt(2))
        self.assertEqual(plug(('helpers', 'math', 'fabs'), 2), fabs(2))

    def test_call2_multiple(self):
        from math import sqrt, fabs
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.math.fabs(2), fabs(2))
        self.assertEqual(plug.helpers.math.sqrt(2), sqrt(2))


class TestQuintuple(unittest.TestCase):

    def _make_multiple(self):
        from math import fabs
        from appspace.builder import AppspaceFactory, App
        return App(AppspaceFactory(
            ('helpers', 'util', 'misc'),
            ('square', 'math.sqrt'),
            ('fabulous', fabs),
            ('formit', 're.match'),
            ('lower', 'string.lowercase'),
            ('upper', 'string.uppercase'),
            ('store', 'UserDict.UserDict'),
        ).appspace)

    def test_init_multiple(self):
        plug = self._make_multiple()
        self.assertEqual('square' in plug['helpers']['util']['misc'], True)
        self.assertEqual('fabulous' in plug['helpers']['util']['misc'], True)
        self.assertEqual('formit' in plug['helpers']['util']['misc'], True)
        self.assertEqual('lower' in plug['helpers']['util']['misc'], True)
        self.assertEqual('upper' in plug['helpers']['util']['misc'], True)
        self.assertEqual('store' in plug['helpers']['util']['misc'], True)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(
            plug.helpers.util.misc.square,
            plug['helpers']['util']['misc']['square']
        )
        self.assertEqual(
            plug.helpers.util.misc.fabulous,
            plug['helpers']['util']['misc']['fabulous']
        )
        self.assertEqual(
            plug.helpers.util.misc.formit,
            plug['helpers']['util']['misc']['formit']
        )
        self.assertEqual(
            plug.helpers.util.misc.lower,
            plug['helpers']['util']['misc']['lower']
        )
        self.assertEqual(
            plug.helpers.util.misc.upper,
            plug['helpers']['util']['misc']['upper']
        )
        self.assertEqual(
            plug.helpers.util.misc.store,
            plug['helpers']['util']['misc']['store']
        )

    def test_identity_namespace(self):
        from appspace.builder import App
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, App)
        self.assertIsInstance(app.helpers.util, App)
        self.assertIsInstance(app.helpers.util.misc, App)

    def test_identity_multiple(self):
        from math import sqrt, fabs
        from re import match
        from string import lowercase, uppercase
        from UserDict import UserDict
        plug = self._make_multiple()
        self.assert_(plug.helpers.util.misc.square is sqrt)
        self.assert_(plug.helpers.util.misc.fabulous is fabs)
        self.assert_(plug.helpers.util.misc.formit is match)
        self.assert_(plug.helpers.util.misc.lower is lowercase)
        self.assert_(plug.helpers.util.misc.upper is uppercase)
        self.assert_(plug.helpers.util.misc.store is UserDict)

    def test_call_multiple(self):
        from math import sqrt, fabs
        from re import match
        from string import lowercase, uppercase
        from UserDict import UserDict
        plug = self._make_multiple()
        self.assertEqual(
            plug(('helpers', 'util', 'misc', 'square'), 2), sqrt(2)
        )
        self.assertEqual(
            plug(('helpers', 'util', 'misc', 'fabulous'), 2), fabs(2)
        )
        self.assertEqual(
            plug(('helpers', 'util', 'misc',  'formit'), '2', '2').string,
            match('2', '2').string
        )
        self.assertEqual(plug(('helpers', 'util', 'misc', 'lower')), lowercase)
        self.assertEqual(plug(('helpers', 'util', 'misc', 'upper')), uppercase)
        self.assert_(
            isinstance(plug(('helpers', 'util', 'misc', 'store')), UserDict)
        )


    def test_call2_multiple(self):
        from re import match
        from math import sqrt, fabs
        from UserDict import UserDict
        from string import lowercase, uppercase
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.util.misc.square(2), sqrt(2))
        self.assertEqual(plug.helpers.util.misc.fabulous(2), fabs(2))
        self.assertEqual(
            plug.helpers.util.misc.formit('2', '2').string,
            match('2', '2').string
        )
        self.assertEqual(plug.helpers.util.misc.lower, lowercase)
        self.assertEqual(plug.helpers.util.misc.upper, uppercase)
        self.assertEqual(plug.helpers.util.misc.store, UserDict)


class TestGlobal(unittest.TestCase):

    def _make_multiple(self):
        from appspace import app
        return app

    def setUp(self):
        from math import fabs
        from appspace import patterns
        patterns(
            ('helpers', 'util', 'misc'),
            ('square', 'math.sqrt'),
            ('fabulous', fabs),
            ('formit', 're.match'),
            ('lower', 'string.lowercase'),
            ('upper', 'string.uppercase'),
            ('store', 'UserDict.UserDict'),
            use_global=True,
        )

    def tearDown(self):
        from zope.component import getSiteManager
        getSiteManager.reset()

    def test_init_multiple(self):
        plug = self._make_multiple()
        self.assertEqual('square' in plug['helpers']['util']['misc'], True)
        self.assertEqual('fabulous' in plug['helpers']['util']['misc'], True)
        self.assertEqual('formit' in plug['helpers']['util']['misc'], True)
        self.assertEqual('lower' in plug['helpers']['util']['misc'], True)
        self.assertEqual('upper' in plug['helpers']['util']['misc'], True)
        self.assertEqual('store' in plug['helpers']['util']['misc'], True)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(
            plug.helpers.util.misc.square,
            plug['helpers']['util']['misc']['square']
        )
        self.assertEqual(
            plug.helpers.util.misc.fabulous,
            plug['helpers']['util']['misc']['fabulous']
        )
        self.assertEqual(
            plug.helpers.util.misc.formit,
            plug['helpers']['util']['misc']['formit']
        )
        self.assertEqual(
            plug.helpers.util.misc.lower,
            plug['helpers']['util']['misc']['lower']
        )
        self.assertEqual(
            plug.helpers.util.misc.upper,
            plug['helpers']['util']['misc']['upper']
        )
        self.assertEqual(
            plug.helpers.util.misc.store,
            plug['helpers']['util']['misc']['store']
        )

    def test_identity_namespace(self):
        from appspace.builder import App
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, App)
        self.assertIsInstance(app.helpers.util, App)
        self.assertIsInstance(app.helpers.util.misc, App)

    def test_identity_multiple(self):
        from UserDict import UserDict
        from math import sqrt, fabs
        from re import match
        from string import lowercase, uppercase
        plug = self._make_multiple()
        self.assert_(plug.helpers.util.misc.square is sqrt)
        self.assert_(plug.helpers.util.misc.fabulous is fabs)
        self.assert_(plug.helpers.util.misc.formit is match)
        self.assert_(plug.helpers.util.misc.lower is lowercase)
        self.assert_(plug.helpers.util.misc.upper is uppercase)
        self.assert_(plug.helpers.util.misc.store is UserDict)

    def test_call_multiple(self):
        from re import match
        from math import sqrt, fabs
        from UserDict import UserDict
        from string import lowercase, uppercase
        plug = self._make_multiple()
        self.assertEqual(
            plug(('helpers', 'util', 'misc', 'square'), 2), sqrt(2)
        )
        self.assertEqual(
            plug(('helpers', 'util', 'misc', 'fabulous'), 2), fabs(2)
        )
        self.assertEqual(
            plug(('helpers', 'util', 'misc',  'formit'), '2', '2').string,
            match('2', '2').string
        )
        self.assertEqual(plug(('helpers', 'util', 'misc', 'lower')), lowercase)
        self.assertEqual(plug(('helpers', 'util', 'misc', 'upper')), uppercase)
        self.assert_(
            isinstance(plug(('helpers', 'util', 'misc', 'store')), UserDict)
        )

    def test_call2_multiple(self):
        from re import match
        from math import sqrt, fabs
        from UserDict import UserDict
        from string import lowercase, uppercase
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.util.misc.square(2), sqrt(2))
        self.assertEqual(plug.helpers.util.misc.fabulous(2), fabs(2))
        self.assertEqual(
            plug.helpers.util.misc.formit('2', '2').string,
            match('2', '2').string
        )
        self.assertEqual(plug.helpers.util.misc.lower, lowercase)
        self.assertEqual(plug.helpers.util.misc.upper, uppercase)
        self.assertEqual(plug.helpers.util.misc.store, UserDict)


class TestAppconf(unittest.TestCase):

    def _make_multiple(self):
        from appspace import app
        return app

    def setUp(self):
        from appspace import appconf, include
        appconf(
            ('helpers', 'util'),
            ('misc', include('appspace.test')),
            use_global=True,
        )

    def tearDown(self):
        from zope.component import getSiteManager
        getSiteManager.reset()

    def test_init_multiple(self):
        plug = self._make_multiple()
        self.assertEqual('square' in plug['helpers']['util']['misc'], True)
        self.assertEqual('fabulous' in plug['helpers']['util']['misc'], True)
        self.assertEqual('formit' in plug['helpers']['util']['misc'], True)
        self.assertEqual('lower' in plug['helpers']['util']['misc'], True)
        self.assertEqual('upper' in plug['helpers']['util']['misc'], True)
        self.assertEqual('store' in plug['helpers']['util']['misc'], True)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(
            plug.helpers.util.misc.square,
            plug['helpers']['util']['misc']['square']
        )
        self.assertEqual(
            plug.helpers.util.misc.fabulous,
            plug['helpers']['util']['misc']['fabulous']
        )
        self.assertEqual(
            plug.helpers.util.misc.formit,
            plug['helpers']['util']['misc']['formit']
        )
        self.assertEqual(
            plug.helpers.util.misc.lower,
            plug['helpers']['util']['misc']['lower']
        )
        self.assertEqual(
            plug.helpers.util.misc.upper,
            plug['helpers']['util']['misc']['upper']
        )
        self.assertEqual(
            plug.helpers.util.misc.store,
            plug['helpers']['util']['misc']['store']
        )

    def test_identity_namespace(self):
        from appspace.builder import App
        app = self._make_multiple()
        self.assertIsInstance(app.helpers, App)
        self.assertIsInstance(app.helpers.util, App)
        self.assertIsInstance(app.helpers.util.misc, App)

    def test_identity_multiple(self):
        from math import sqrt, fabs
        from re import match
        from string import lowercase, uppercase
        from UserDict import UserDict
        plug = self._make_multiple()
        self.assert_(plug.helpers.util.misc.square is sqrt)
        self.assert_(plug.helpers.util.misc.fabulous is fabs)
        self.assert_(plug.helpers.util.misc.formit is match)
        self.assert_(plug.helpers.util.misc.lower is lowercase)
        self.assert_(plug.helpers.util.misc.upper is uppercase)
        self.assert_(plug.helpers.util.misc.store is UserDict)

    def test_call_multiple(self):
        from re import match
        from math import sqrt, fabs
        from UserDict import UserDict
        from string import lowercase, uppercase
        plug = self._make_multiple()
        self.assertEqual(
            plug(('helpers', 'util', 'misc', 'square'), 2), sqrt(2)
        )
        self.assertEqual(
            plug(('helpers', 'util', 'misc', 'fabulous'), 2), fabs(2)
        )
        self.assertEqual(
            plug(('helpers', 'util', 'misc',  'formit'), '2', '2').string,
            match('2', '2').string
        )
        self.assertEqual(plug(('helpers', 'util', 'misc', 'lower')), lowercase)
        self.assertEqual(plug(('helpers', 'util', 'misc', 'upper')), uppercase)
        self.assert_(
            isinstance(plug(('helpers', 'util', 'misc', 'store')), UserDict)
        )

    def test_call2_multiple(self):
        from re import match
        from math import sqrt, fabs
        from UserDict import UserDict as UD
        from string import lowercase, uppercase
        plug = self._make_multiple()
        self.assertEqual(plug.helpers.util.misc.square(2), sqrt(2))
        self.assertEqual(plug.helpers.util.misc.fabulous(2), fabs(2))
        self.assertEqual(
            plug.helpers.util.misc.formit('2', '2').string,
            match('2', '2').string
        )
        self.assertEqual(plug.helpers.util.misc.lower, lowercase)
        self.assertEqual(plug.helpers.util.misc.upper, uppercase)
        self.assertEqual(plug.helpers.util.misc.store, UD)


class TestAltAppKey(unittest.TestCase):

    def _make_multiple(self):
        from appspace.test.classtest import ATestClass
        from appspace import appconf
        return appconf(
            'classtest',
            ('one', 'appspace.test.classtest.testclass.footrain'),
            ('two', 'appspace.test.classtest.testclass.rootrain'),
            ('three', 'appspace.test.classtest.testclass.bahrain'),
            app=ATestClass,
        )

    def test_init_multiple(self):
        plug = self._make_multiple()
        self.assertEqual('one' in plug['classtest'], True)
        self.assertEqual('two' in plug['classtest'], True)
        self.assertEqual('three' in plug['classtest'], True)

    def test_attr_multiple(self):
        plug = self._make_multiple()
        self.assertEqual(plug.one, plug['classtest']['one'])
        self.assertEqual(plug.two, plug['classtest']['two'])
        self.assertEqual(plug.three, plug['classtest']['three'])

    def test_identity_namespace(self):
        from appspace.builder import App
        app = self._make_multiple()
        self.assertIsInstance(app.classtest, App)

    def test_call_multiple(self):
        from appspace.test.classtest import testclass
        plug = self._make_multiple()
        self.assertEqual(plug('one', 2), testclass.footrain(2))
        self.assertEqual(plug('two', 2), testclass.rootrain(2))
        self.assertEqual(plug('two', 2), testclass.bahrain(2))

    def test_call2_multiple(self):
        from appspace.test.classtest import testclass
        plug = self._make_multiple()
        self.assertEqual(plug.one(2), testclass.footrain(2))
        self.assertEqual(plug.two(2), testclass.rootrain(2))
        self.assertEqual(plug.three(2), testclass.bahrain(2))



if __name__ == '__main__':
    unittest.main()