import unittest

import numpy
from numpy import testing
import lxMath


class TestV2f(unittest.TestCase):
    def setUp(self):
        self.v2f = None
        self.v2f_b = None
        self.v2f_r = None

    def tearDown(self):

        # last safety checks
        if self.v2f_b is not None:
            self.assertIsInstance(self.v2f_b, lxMath.V2f)

        if self.v2f_r is not None:
            self.assertIsInstance(self.v2f_r, lxMath.V2f)

        # clean
        self.v2f = None
        self.v2f_b = None
        self.v2f_r = None

        return

    def log(self):
        out = f"{'='*99}\n[{self.id()}] Started\n---------\n"
        out += f"v2f = {self.v2f}\n"
        out += f"v2f_b = {self.v2f_b}\n"
        out += f"v2f_r = {self.v2f_r}\n"
        print(out)

    def test_basic(self):

        self.v2f = lxMath.V2f(0.3, 0.1)

        self.log()
        self.assertEqual(self.v2f.x, 0.3)
        self.assertEqual(self.v2f.y, 0.1)

    def test_init_arg_solo(self):

        self.v2f = lxMath.V2f(0.3)
        self.log()
        self.assertEqual(self.v2f.x, 0.3)
        self.assertEqual(self.v2f.y, 0.3)

        self.v2f = lxMath.V2f(1.6)
        self.log()
        self.assertEqual(self.v2f.x, 1.6)
        self.assertEqual(self.v2f.y, 1.6)

    def test_basic_kwarg_xy(self):

        self.v2f = lxMath.V2f(x=0.3, y=0.1)

        self.log()
        self.assertEqual(self.v2f.x, 0.3)
        self.assertEqual(self.v2f.y, 0.1)

    def test_basic_kwarg_array(self):

        self.v2f = lxMath.V2f(array=numpy.array((1920, 1080)))
        self.log()
        self.assertEqual(self.v2f.x, 1920)
        self.assertEqual(self.v2f.y, 1080)

    def test_basic_kwarg_error(self):

        with self.assertRaises(ValueError) as excp:
            lxMath.V2f(0.5, y=35)

    def test_default(self):

        self.v2f = lxMath.V2f()

        self.log()
        self.assertEqual(self.v2f.x, 0.0)
        self.assertEqual(self.v2f.y, 0.0)

    def test_default_kwarg(self):

        self.v2f = lxMath.V2f(array=None)

        self.log()
        self.assertEqual(self.v2f.x, 0.0)
        self.assertEqual(self.v2f.y, 0.0)

    def test_instance(self):

        self.v2f = lxMath.V2f(0.3, 0.1)
        self.v2f_b = lxMath.V2f(self.v2f)

        self.log()
        self.assertEqual(self.v2f_b.x, 0.3)
        self.assertEqual(self.v2f_b.y, 0.1)

        self.assertIsNot(self.v2f, self.v2f_b)
        testing.assert_array_equal(self.v2f, self.v2f_b)

    def test_instance_kwargs(self):

        self.v2f = lxMath.V2f(0.3, 0.1)
        self.v2f_b = lxMath.V2f(array=self.v2f)

        self.log()
        self.assertEqual(self.v2f_b.x, 0.3)
        self.assertEqual(self.v2f_b.y, 0.1)

        self.assertIsNot(self.v2f, self.v2f_b)
        testing.assert_array_equal(self.v2f, self.v2f_b)

    def test_mul(self):

        self.v2f = lxMath.V2f(0.3, 0.1)
        self.v2f_r = self.v2f * 2

        self.log()
        self.assertEqual(0.6, self.v2f_r.x)
        self.assertEqual(0.2, self.v2f_r.y)

        self.assertIsNot(self.v2f, self.v2f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v2f, self.v2f_r)

    def test_mul_neg(self):

        self.v2f = lxMath.V2f(0.3, 0.1)
        self.v2f_r = self.v2f * -2

        self.log()
        self.assertEqual(-0.6, self.v2f_r.x)
        self.assertEqual(-0.2, self.v2f_r.y)

    def test_mul_instance(self):

        self.v2f = lxMath.V2f(0.3, 0.1)
        self.v2f_b = lxMath.V2f(10, 0.5)
        self.v2f_r = self.v2f * self.v2f_b

        self.log()
        self.assertEqual(3.0, self.v2f_r.x)
        self.assertEqual(0.05, self.v2f_r.y)

        self.assertIsNot(self.v2f, self.v2f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v2f, self.v2f_r)

    def test_div(self):

        self.v2f = lxMath.V2f(0.3, 0.1)
        self.v2f_r = self.v2f / 2

        self.log()
        self.assertEqual(0.15, self.v2f_r.x)
        self.assertEqual(0.05, self.v2f_r.y)

        self.assertIsNot(self.v2f, self.v2f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v2f, self.v2f_r)

    def test_div_instance(self):

        self.v2f = lxMath.V2f(10, 0.5)
        self.v2f_b = lxMath.V2f(5, 3.6)
        self.v2f_r = self.v2f / self.v2f_b

        self.log()
        self.assertEqual(10 / 5, self.v2f_r.x)
        self.assertEqual(0.5 / 3.6, self.v2f_r.y)

        self.assertIsNot(self.v2f, self.v2f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v2f, self.v2f_r)

    def test_add(self):

        self.v2f = lxMath.V2f(0.3, 0.1)
        self.v2f_r = self.v2f + 2.5

        self.log()
        self.assertEqual(0.3 + 2.5, self.v2f_r.x)
        self.assertEqual(0.1 + 2.5, self.v2f_r.y)

        self.assertIsNot(self.v2f, self.v2f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v2f, self.v2f_r)


class TestV3f(unittest.TestCase):
    def setUp(self):
        self.v3f = None
        self.v3f_b = None
        self.v3f_r = None

    def tearDown(self):

        # last safety checks
        if self.v3f_b is not None:
            self.assertIsInstance(self.v3f_b, lxMath.V3f)

        if self.v3f_r is not None:
            self.assertIsInstance(self.v3f_r, lxMath.V3f)

        # clean
        self.v3f = None
        self.v3f_b = None
        self.v3f_r = None

        return

    def log(self):
        out = f"{'='*99}\n[{self.id()}] Started\n---------\n"
        out += f"v3f = {self.v3f}\n"
        out += f"v3f_b = {self.v3f_b}\n"
        out += f"v3f_r = {self.v3f_r}\n"
        print(out)

    def test_basic(self):

        self.v3f = lxMath.V3f(0.3, 0.1, 12)
        self.log()
        self.assertEqual(self.v3f.x, 0.3)
        self.assertEqual(self.v3f.y, 0.1)
        self.assertEqual(self.v3f.z, 12)

    def test_init_arg_solo(self):

        self.v3f = lxMath.V3f(0.3)
        self.log()
        self.assertEqual(self.v3f.x, 0.3)
        self.assertEqual(self.v3f.y, 0.3)
        self.assertEqual(self.v3f.z, 0.3)

        self.v3f = lxMath.V3f(1.6)
        self.log()
        self.assertEqual(self.v3f.x, 1.6)
        self.assertEqual(self.v3f.y, 1.6)
        self.assertEqual(self.v3f.z, 1.6)

    def test_default(self):

        self.v3f = lxMath.V3f()

        self.log()
        self.assertEqual(self.v3f.x, 0.0)
        self.assertEqual(self.v3f.y, 0.0)
        self.assertEqual(self.v3f.z, 0.0)

    def test_instance(self):

        self.v3f = lxMath.V3f(0.3, 0.1, 12)
        self.v3f_b = lxMath.V3f(self.v3f)

        self.log()
        self.assertEqual(self.v3f_b.x, 0.3)
        self.assertEqual(self.v3f_b.y, 0.1)
        self.assertEqual(self.v3f_b.z, 12)

        self.assertIsNot(self.v3f, self.v3f_b)
        testing.assert_array_equal(self.v3f, self.v3f_b)

    def test_mul(self):

        self.v3f = lxMath.V3f(0.3, 0.1, 12)
        self.v3f_r = self.v3f * 2

        self.log()
        self.assertEqual(0.6, self.v3f_r.x)
        self.assertEqual(0.2, self.v3f_r.y)
        self.assertEqual(24, self.v3f_r.z)

        self.assertIsNot(self.v3f, self.v3f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v3f, self.v3f_r)

    def test_mul_neg(self):

        self.v3f = lxMath.V3f(0.3, 0.1, 12)
        self.v3f_r = self.v3f * -2

        self.log()
        self.assertEqual(-0.6, self.v3f_r.x)
        self.assertEqual(-0.2, self.v3f_r.y)
        self.assertEqual(-24, self.v3f_r.z)

    def test_mul_instance(self):

        self.v3f = lxMath.V3f(0.3, 0.1, 12)
        self.v3f_b = lxMath.V3f(10, 0.5, 0.5)
        self.v3f_r = self.v3f * self.v3f_b

        self.log()
        self.assertEqual(3.0, self.v3f_r.x)
        self.assertEqual(0.05, self.v3f_r.y)
        self.assertEqual(6, self.v3f_r.z)

        self.assertIsNot(self.v3f, self.v3f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v3f, self.v3f_r)

    def test_div(self):

        self.v3f = lxMath.V3f(0.3, 0.1, 12)
        self.v3f_r = self.v3f / 2

        self.log()
        self.assertEqual(0.15, self.v3f_r.x)
        self.assertEqual(0.05, self.v3f_r.y)
        self.assertEqual(6.0, self.v3f_r.z)

        self.assertIsNot(self.v3f, self.v3f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v3f, self.v3f_r)

    def test_div_instance(self):

        self.v3f = lxMath.V3f(10, 0.5, -0.3)
        self.v3f_b = lxMath.V3f(5, 3.6, 0.5)
        self.v3f_r = self.v3f / self.v3f_b

        self.log()
        self.assertEqual(10 / 5, self.v3f_r.x)
        self.assertEqual(0.5 / 3.6, self.v3f_r.y)
        self.assertEqual(-0.3 / 0.5, self.v3f_r.z)

        self.assertIsNot(self.v3f, self.v3f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v3f, self.v3f_r)

    def test_add(self):

        self.v3f = lxMath.V3f(0.3, 0.1, 12)
        self.v3f_r = self.v3f + 2.5

        self.log()
        self.assertEqual(0.3 + 2.5, self.v3f_r.x)
        self.assertEqual(0.1 + 2.5, self.v3f_r.y)
        self.assertEqual(12 + 2.5, self.v3f_r.z)

        self.assertIsNot(self.v3f, self.v3f_r)
        with self.assertRaises(AssertionError) as excp:
            testing.assert_array_equal(self.v3f, self.v3f_r)


if __name__ == "__main__":
    unittest.main()
