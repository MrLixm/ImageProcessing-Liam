"""
"""

import unittest

from PIL import Image

import imageGridCombine as iGC


class TestImageGridPart(unittest.TestCase):
    def setUp(self):
        self.log()

        self.imggc0x0 = iGC.ImageGridPart(0, 0, Image.new("RGB", (16, 16)))
        self.imggc0x1 = iGC.ImageGridPart(0, 1, Image.new("RGB", (16, 16)))
        self.imggc0x2 = iGC.ImageGridPart(0, 2, Image.new("RGB", (16, 16)))
        self.imggc1x0 = iGC.ImageGridPart(1, 0, Image.new("RGB", (16, 16)))
        self.imggc1x1 = iGC.ImageGridPart(1, 1, Image.new("RGB", (16, 16)))
        self.imggc1x2 = iGC.ImageGridPart(1, 2, Image.new("RGB", (16, 16)))

        print(f"//{'-'*50}")
        return

    def tearDown(self):

        self.imggc0x0 = None
        self.imggc0x1 = None
        self.imggc0x2 = None
        self.imggc1x0 = None
        self.imggc1x1 = None
        self.imggc1x2 = None

        return

    def log(self):
        print(
            "\n\n//{}\n"
            "//    Starting Test : {}\n"
            "// {}".format("=" * 99, self.id(), "-" * 99)
        )
        return

    def test_operators(self):

        self.assertTrue(self.imggc0x2 > self.imggc1x2)
        self.assertTrue(self.imggc0x2 > self.imggc0x1)
        self.assertTrue(self.imggc1x0 < self.imggc1x1)
        self.assertFalse(self.imggc1x2 < self.imggc1x1)
        self.assertTrue(self.imggc0x0 <= self.imggc0x0)
        self.assertFalse(self.imggc0x0 <= self.imggc1x0)
        self.assertFalse(self.imggc0x1 >= self.imggc1x2)
        self.assertTrue(self.imggc1x1 >= self.imggc1x1)
        self.assertTrue(self.imggc1x2 >= self.imggc1x0)

        self.assertTrue(self.imggc1x1 == self.imggc1x1)
        self.assertFalse(self.imggc1x0 == self.imggc1x1)

        return


if __name__ == "__main__":

    unittest.main()
