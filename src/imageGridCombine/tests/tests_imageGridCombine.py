"""
"""
import logging
import unittest
from pathlib import Path

from PIL import Image

import imageGridCombine as iGC

logger = logging.getLogger("iGC.tests.tests_imageGridCombine")


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


class TestImageResult(unittest.TestCase):
    def setUp(self):
        self.log()

    def log(self):
        print(
            "\n\n//{}\n"
            "//    Starting Test : {}\n"
            "// {}".format("=" * 99, self.id(), "-" * 99)
        )
        return

    def test1(self):

        source_dir = Path("./img/test1")
        sources_version = "0001"
        extension = "jpg"
        target_path = source_dir / f"combined.{sources_version}.{extension}"
        regex = rf".+\.{sources_version}\.(\d)+x(\d)+"

        sources_list = iGC.utilities.get_specific_files_from_dir(
            directory=source_dir,
            extension=extension,
            regex=regex,
        )
        self.assertIsNotNone(sources_list, f"No file found in directory {source_dir}")
        _ = "\n".join([f"    - {fp}" for fp in sources_list])
        logger.info(f"[test1] Found {len(sources_list)} images to combine :\n{_}")
        del _

        img = iGC.utilities.combine_from_nuke(sources_list=sources_list)
        iGC.utilities.write_jpg(img, export_path=target_path)

        self.assertTrue(target_path.exists())

        return

    def test2(self):

        source_dir = Path("./img/test2")
        sources_version = "0001"
        extension = "jpg"
        target_path = source_dir / f"combined.{sources_version}.{extension}"
        regex = rf".+\.{sources_version}\.(\d)+x(\d)+"

        sources_list = iGC.utilities.get_specific_files_from_dir(
            directory=source_dir,
            extension=extension,
            regex=regex,
        )
        self.assertIsNotNone(sources_list, f"No file found in directory {source_dir}")
        _ = "\n".join([f"    - {fp}" for fp in sources_list])
        logger.info(f"[test1] Found {len(sources_list)} images to combine :\n{_}")
        del _

        img = iGC.utilities.combine_from_nuke(sources_list=sources_list)
        iGC.utilities.write_jpg(img, export_path=target_path)

        self.assertTrue(target_path.exists())

        return


if __name__ == "__main__":

    unittest.main()
