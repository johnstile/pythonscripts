#!/usr/bin/env python

import unittest


class SimplisticTest(unittest.TestCase):
    def test(self):
        self.assertTrue(True, 'failure message goes here')


class OutcomesTest(unittest.TestCase):
    def testPass(self):
        return

    def testFail(self):
        self.assertFalse(True, 'failure message goes here')

    def testError(self):
        raise RuntimeError('Test error!')


class TruthTest(unittest.TestCase):
    """"truth-checking tests
    """
    def testFailUnless(self):
        self.assertTrue(True)

    def testAssertTrue(self):
        self.assertTrue(True)

    def testFailIf(self):
        self.assertFalse(False)

    def testAssertFalse(self):
        self.assertFalse(False)


class EqualityTest(unittest.TestCase):

    def testEqual(self):
        self.assertEqual(1, 3-2)

    def testNotEqual(self):
        self.assertNotEqual(2, 3-2)        


class InequalityTest(unittest.TestCase):

    def testEqual(self):
        self.assertNotEqual(1, 3-2)

    def testNotEqual(self):
        self.assertEqual(2, 3-2)


class AlmostEqualTest(unittest.TestCase):

    def testNotAlmostEqual(self):
        self.assertNotAlmostEqual(1.1, 3.3-2.0, places=1)

    def testAlmostEqual(self):
        self.assertAlmostEqual(1.1, 3.3-2.0, places=0)

class FixturesTest(unittest.TestCase):
    """Test Fixtures are resources needed by a test
    like a database connections or temporary file.

    Some say external dependencies are not “unit” tests

    TestCase will automaticly cleaup if you  
    override: setUp() and tearDown() 
     
    """

    def setUp(self):
        print('In setUp()')
        self.fixture = range(1, 10)

    def tearDown(self):
        print('In tearDown()')
        del self.fixture

    def test(self):
        print('in test()')
        self.assertEqual(self.fixture, range(1, 10))

 

if __name__ == '__main__':
    unittest.main()

