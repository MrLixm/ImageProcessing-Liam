"""
[LICENSE]
Copyright 2022 Liam Collod
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
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
        self.assertTrue(self.imggc0x2 < self.imggc0x1)
        self.assertTrue(self.imggc1x0 > self.imggc1x1)
        self.assertFalse(self.imggc1x2 > self.imggc1x1)
        self.assertTrue(self.imggc0x0 <= self.imggc0x0)
        self.assertFalse(self.imggc0x0 <= self.imggc1x0)
        self.assertFalse(self.imggc0x1 <= self.imggc1x2)
        self.assertTrue(self.imggc1x1 >= self.imggc1x1)
        self.assertFalse(self.imggc1x2 >= self.imggc1x0)

        self.assertTrue(self.imggc1x1 == self.imggc1x1)
        self.assertFalse(self.imggc1x0 == self.imggc1x1)

        return


class TestImageResult(unittest.TestCase):
    def setUp(self):

        self.log()

        dirname = self.id().split(".")[-1]

        source_dir = Path(f"./img/{dirname}")
        sources_version = "0001"
        extension = "jpg"
        regex = rf".+\.{sources_version}\.(\d)+x(\d)+"

        self.target_path = source_dir / f"combined.{sources_version}.{extension}"

        self.sources_list = iGC.utilities.get_specific_files_from_dir(
            directory=source_dir,
            extension=extension,
            regex=regex,
        )

        self.assertIsNotNone(
            self.sources_list, f"No file found in directory {source_dir}"
        )

        _ = "\n".join([f"    - {fp}" for fp in self.sources_list])
        print(f"Found {len(self.sources_list)} images to combine :\n{_}")
        del _

        return

    def tearDown(self):

        # delete the created file
        self.target_path.unlink(missing_ok=True)

        self.sources_list = None
        self.target_path = None
        return

    def log(self):
        print(
            "\n\n//{}\n"
            "//    Starting Test : {}\n"
            "// {}".format("=" * 99, self.id(), "-" * 99)
        )
        return

    def test1(self):

        imggrid = iGC.ImageGrid.build_from_paths(
            paths_list=self.sources_list,
            crop_data_function=iGC.utilities.extract_crop_data,
        )
        imggrid.reverse_rows()
        imggrid.write_to(export_path=self.target_path, quality=95, subsampling=0)

        self.assertTrue(self.target_path.exists())

        return

    def test2(self):

        imggrid = iGC.ImageGrid.build_from_paths(
            paths_list=self.sources_list,
            crop_data_function=iGC.utilities.extract_crop_data,
        )
        imggrid.reverse_rows()
        imggrid.write_to(export_path=self.target_path, quality=95, subsampling=0)

        self.assertTrue(self.target_path.exists())

        return


if __name__ == "__main__":

    unittest.main()
