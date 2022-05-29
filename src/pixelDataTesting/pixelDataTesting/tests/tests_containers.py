import unittest
from pathlib import Path

import pixelDataTesting as pxdt

DRAGONFILENAME = "dragonScene.0001.base.aces.half.1001.exr"


class TestTestAsset(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_manual(self):

        ta = pxdt.TestAsset(pxdt.c.DATA_DIR / "dragonScene")
        ti_first = pxdt.TestImage(
            parent=ta,
            relative_path=Path(DRAGONFILENAME),
        )

        self.assertEqual(ta.path, pxdt.c.DATA_DIR / "dragonScene")
        self.assertEqual(ta.id, "dragonScene")
        self.assertEqual(ta.first, ti_first)


class TestTestImage(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_manual(self):

        with self.assertRaises(FileNotFoundError):
            ta = pxdt.TestAsset(Path("TEST"))

        ta = pxdt.TestAsset(pxdt.c.DATA_DIR / "dragonScene")
        ti = pxdt.TestImage(
            parent=ta,
            relative_path=Path(DRAGONFILENAME),
        )

        self.assertEqual(ti.path, ta.path / DRAGONFILENAME)
        self.assertEqual(ti.id, "0001")
        self.assertEqual(ti.variant, "base")
        self.assertEqual(ti.colorspace, "aces")
        self.assertEqual(ti.size, "half")
        self.assertEqual(ti.ext, ".exr")


if __name__ == "__main__":
    unittest.main()
