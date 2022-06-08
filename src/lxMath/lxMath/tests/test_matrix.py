"""

"""
import unittest

import numpy
from numpy import testing

import lxMath


class TestM33f(unittest.TestCase):
    def setUp(self):
        self.m33f = None
        self.m33f_b = None
        self.m33f_r = None
        self.array_a = None
        self.array_b = None
        self.result_a = None

    def tearDown(self):

        # last safety checks
        if self.m33f_b is not None:
            self.assertIsInstance(self.m33f_b, lxMath.M33f)

        if self.m33f_r is not None:
            self.assertIsInstance(self.m33f_r, lxMath.M33f)

        # clean
        self.m33f = None
        self.m33f_b = None
        self.m33f_r = None
        self.array_a = None
        self.array_b = None
        self.result_a = None

        return

    def log(self):
        def getMsg(attrname):
            attr = self.__getattribute__(attrname)
            return (
                f"{'_'*50}\n<{attrname}>{type(attr)}\n {attr}\n"
                if attr is not None
                else ""
            )

        attrs = [
            "m33f",
            "m33f_b",
            "array_a",
            "array_b",
            "m33f_r",
            "result_a",
        ]
        out = f"\n{'='*99}\n[{self.id()}] Started\n"
        for attr_name in attrs:
            out += getMsg(attr_name)

        print(out)

    def test_basic(self):

        matrix_a = [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
        self.m33f = lxMath.M33f(matrix_a)

        self.log()
        testing.assert_array_equal(self.m33f, matrix_a.copy())

    def test_9args(self):

        matrix_a = [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
        self.m33f = lxMath.M33f(
            0.4124564,
            0.3575761,
            0.1804375,
            0.2126729,
            0.7151522,
            0.0721750,
            0.0193339,
            0.1191920,
            0.9503041,
        )

        self.log()
        testing.assert_array_equal(self.m33f, matrix_a)

    def test_default(self):

        self.m33f = lxMath.M33f()
        equal = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        equal2 = numpy.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        self.log()
        testing.assert_array_equal(self.m33f, equal)
        testing.assert_array_equal(self.m33f, equal2)

    def test_mul_list(self):

        self.m33f = lxMath.M33f()
        self.array_a = [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]

        self.m33f_r = self.m33f * self.array_a.copy()

        self.log()
        testing.assert_array_equal(self.m33f_r, self.array_a)

    def test_mul_scalar(self):

        self.m33f = lxMath.M33f()

        self.m33f_r = self.m33f * 5

        self.log()
        testing.assert_array_equal(
            self.m33f_r,
            [[5.0, 0.0, 0.0], [0.0, 5.0, 0.0], [0.0, 0.0, 5.0]],
        )

    def test_rmul_list(self):

        self.m33f = lxMath.M33f()
        self.array_a = [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]

        self.m33f_r = self.array_a.copy() * self.m33f

        self.log()
        testing.assert_array_equal(self.m33f_r, self.array_a)

    def test_make_identity(self):

        self.array_a = [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
        self.m33f = lxMath.M33f(self.array_a)
        self.m33f.makeIdentity()
        equal = numpy.identity(3)

        self.log()
        testing.assert_array_equal(self.m33f, equal)

    def test_is_identity(self):

        self.array_a = [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
        self.m33f = lxMath.M33f(self.array_a)
        self.m33f.makeIdentity()

        self.log()
        self.assertTrue(self.m33f.isIdentity())

    def test_array_memory(self):

        self.array_a = numpy.array(
            [
                [0.4124564, 0.3575761, 0.1804375],
                [0.2126729, 0.7151522, 0.0721750],
                [0.0193339, 0.1191920, 0.9503041],
            ]
        )
        self.m33f = lxMath.M33f(self.array_a)
        self.array_a[:] = numpy.identity(3)

        self.log()
        self.assertTrue(self.m33f.isIdentity())

    def test_to_m44(self):
        equal = numpy.array(
            [
                [0.4124564, 0.3575761, 0.1804375, 0],
                [0.2126729, 0.7151522, 0.0721750, 0],
                [0.0193339, 0.1191920, 0.9503041, 0],
                [0, 0, 0, 1],
            ]
        )
        self.array_a = numpy.array(
            [
                [0.4124564, 0.3575761, 0.1804375],
                [0.2126729, 0.7151522, 0.0721750],
                [0.0193339, 0.1191920, 0.9503041],
            ]
        )
        self.m33f = lxMath.M33f(self.array_a)
        self.result_a = self.m33f.to_m44f()
        self.log()
        self.assertIsInstance(self.result_a, lxMath.M44f)
        testing.assert_array_equal(self.result_a, equal)
        return


class TestM44f(unittest.TestCase):
    def setUp(self):
        self.m44f = None
        self.m44f_b = None
        self.m44f_r = None
        self.array_a = None
        self.array_b = None
        self.result_a = None

    def tearDown(self):

        # last safety checks
        if self.m44f_b is not None:
            self.assertIsInstance(self.m44f_b, lxMath.M44f)

        if self.m44f_r is not None:
            self.assertIsInstance(self.m44f_r, lxMath.M44f)

        # clean
        self.m44f = None
        self.m44f_b = None
        self.m44f_r = None
        self.array_a = None
        self.array_b = None
        self.result_a = None

        return

    def log(self):
        def getMsg(attrname):
            attr = self.__getattribute__(attrname)
            return (
                f"{'_'*50}\n<{attrname}>{type(attr)}\n {attr}\n"
                if attr is not None
                else ""
            )

        attrs = [
            "m44f",
            "m44f_b",
            "array_a",
            "array_b",
            "m44f_r",
            "result_a",
        ]
        out = f"\n{'='*99}\n[{self.id()}] Started\n"
        for attr_name in attrs:
            out += getMsg(attr_name)

        print(out)

    def test_basic(self):

        matrix_a = [
            [0.4124564, 0.3575761, 0.1804375, 0],
            [0.2126729, 0.7151522, 0.0721750, 0],
            [0.0193339, 0.1191920, 0.9503041, 0],
            [0.0256314, 0.1292014, 0.4234789, 1],
        ]
        self.m44f = lxMath.M44f(matrix_a)

        self.log()
        testing.assert_array_equal(self.m44f, matrix_a.copy())

    def test_16args(self):

        matrix_a = [
            [0.4124564, 0.3575761, 0.1804375, 0],
            [0.2126729, 0.7151522, 0.0721750, 0],
            [0.0193339, 0.1191920, 0.9503041, 0],
            [0.0256314, 0.1292014, 0.4234789, 1],
        ]
        self.m44f = lxMath.M44f(
            0.4124564,
            0.3575761,
            0.1804375,
            0,
            0.2126729,
            0.7151522,
            0.0721750,
            0,
            0.0193339,
            0.1191920,
            0.9503041,
            0,
            0.0256314,
            0.1292014,
            0.4234789,
            1,
        )

        self.log()
        testing.assert_array_equal(self.m44f, matrix_a)

    def test_default(self):

        self.m44f = lxMath.M44f()
        equal = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        equal2 = numpy.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

        self.log()
        testing.assert_array_equal(self.m44f, equal)
        testing.assert_array_equal(self.m44f, equal2)

    def test_mul_array(self):

        self.m44f = lxMath.M44f()
        self.array_a = numpy.array(
            [
                [0.4124564, 0.3575761, 0.1804375, 0],
                [0.2126729, 0.7151522, 0.0721750, 0],
                [0.0193339, 0.1191920, 0.9503041, 0],
                [0.0256314, 0.1292014, 0.4234789, 1],
            ]
        )

        self.m44f_r = self.m44f * self.array_a.copy()

        self.log()
        testing.assert_array_equal(self.m44f_r, self.array_a)

    def test_mul_scalar(self):

        self.m44f = lxMath.M44f()

        self.m44f_r = self.m44f * 5

        self.log()
        testing.assert_array_equal(
            self.m44f_r,
            [
                [5.0, 0.0, 0.0, 0.0],
                [0.0, 5.0, 0.0, 0.0],
                [0.0, 0.0, 5.0, 0.0],
                [0.0, 0.0, 0.0, 5.0],
            ],
        )

    # def test_rmul_list(self):
    #
    #     self.m44f = lxMath.M33f()
    #     self.array_a = [
    #         [0.4124564, 0.3575761, 0.1804375],
    #         [0.2126729, 0.7151522, 0.0721750],
    #         [0.0193339, 0.1191920, 0.9503041],
    #     ]
    #
    #     self.m44f_r = self.array_a.copy() * self.m44f
    #
    #     self.log()
    #     testing.assert_array_equal(self.m44f_r, self.array_a)
    #
    def test_make_identity(self):

        self.array_a = [
            [0.4124564, 0.3575761, 0.1804375, 0],
            [0.2126729, 0.7151522, 0.0721750, 0],
            [0.0193339, 0.1191920, 0.9503041, 0],
            [0.0256314, 0.1292014, 0.4234789, 1],
        ]
        self.m44f = lxMath.M44f(self.array_a)
        self.m44f.makeIdentity()
        equal = numpy.identity(4)

        self.log()
        testing.assert_array_equal(self.m44f, equal)

    def test_is_identity(self):

        self.array_a = [
            [0.4124564, 0.3575761, 0.1804375, 0],
            [0.2126729, 0.7151522, 0.0721750, 0],
            [0.0193339, 0.1191920, 0.9503041, 0],
            [0.0256314, 0.1292014, 0.4234789, 1],
        ]
        self.m44f = lxMath.M44f(self.array_a)
        self.m44f.makeIdentity()

        self.log()
        self.assertTrue(self.m44f.isIdentity())

    def test_array_memory(self):

        self.array_a = numpy.array(
            [
                [0.4124564, 0.3575761, 0.1804375, 0],
                [0.2126729, 0.7151522, 0.0721750, 0],
                [0.0193339, 0.1191920, 0.9503041, 0],
                [0.0256314, 0.1292014, 0.4234789, 1],
            ]
        )
        self.m44f = lxMath.M44f(self.array_a)
        self.array_a[:] = numpy.identity(4)

        self.log()
        self.assertTrue(self.m44f.isIdentity())


if __name__ == "__main__":
    unittest.main()
