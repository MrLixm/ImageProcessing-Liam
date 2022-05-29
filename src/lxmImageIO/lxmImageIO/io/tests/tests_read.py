"""

"""
import unittest

import pixelDataTesting as pxtd
import lxmImageIO as liio


class TestReadToImage(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dragonscene(self):

        img = liio.io.read.readToImage(
            source=pxtd.dragonScene.first.path,
            colorspace=None,
        )

        self.assertIsInstance(img, liio.containers.ImageContainer)
        self.assertEqual(img.width, 960)
        self.assertEqual(img.height, 540)
        self.assertEqual(img.channels, 3)
        self.assertEqual(img.path, pxtd.dragonScene.first.path)
        self.assertEqual(img.colorspace, None)
        self.assertEqual(img.array.shape[1], img.width)
        self.assertEqual(img.array.shape[0], img.height)
        self.assertEqual(img.array.shape[2], img.channels)


if __name__ == "__main__":
    unittest.main()
