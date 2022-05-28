import unittest
from functools import partial
from pathlib import Path

import PyOpenColorIO as ocio
import colour.io

import OCIOexperiments as ocex
from OCIOexperiments.grading import processes


REMOVE_WRITES = True


class TestOcioOperationGraph(unittest.TestCase):
    def test_init(self):
        # Must not raise anything

        config_path = ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio"
        oog = processes.OcioOperationGraph(config=config_path)

        config = ocio.Config().CreateFromFile(str(config_path))
        oog = processes.OcioOperationGraph(config=config_path)

        self.assertRaises(Exception, partial(processes.OcioOperationGraph, "C:"))

        return


class TestOcioOperationGraphAgx(unittest.TestCase):

    config_path = ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio"

    def setUp(self):
        self.oog = processes.OcioOperationGraph(config=self.config_path)
        img = ocex.c.DATA_DIR / "renders" / "dragonscene_ap0.half.1001.exr"
        self.img_render = colour.io.read_image(str(img))
        return

    def tearDown(self):
        self.oog = None
        self.img_render = None
        return

    def _apply_proc_n_write(self):

        proc = self.oog.get_proc()
        proc: ocio.CPUProcessor = proc.getDefaultCPUProcessor()

        proc.applyRGB(self.img_render)

        out_path = Path(__file__).parent / "_outputs" / f"dragonscene.{self.id()}.jpg"
        colour.io.write_image(self.img_render, str(out_path))
        self.assertTrue(out_path.exists())

        if REMOVE_WRITES:
            out_path.unlink()

        return

    def test_proc1(self):

        self.assertRaises(AssertionError, self.oog.get_proc)

        self.oog.input_encoding = "sRGB"
        self.oog.target_display = "sRGB"
        # self.oog.target_view = "AgX"

        self.assertRaises(AssertionError, self.oog.get_proc)

        return

    def test_proc2(self):

        self.oog.input_encoding = "sRGB"
        self.oog.target_display = "sRGB"
        self.oog.target_view = "BABABOEI"

        self.assertRaises(AssertionError, self.oog.get_proc)

        return

    def test_proc3(self):

        self.oog.input_encoding = "Linear sRGB"
        self.oog.target_display = "sRGB"
        self.oog.target_view = "AgX"
        self.oog.target_looks = "Punchy"

        self.oog.grading.exposure = 0.5
        self.oog.grading.saturation = 1.2

        self.oog.get_proc()

        return

    def test_write(self):

        self.oog.input_encoding = "ACES2065-1"
        self.oog.target_display = "sRGB"
        self.oog.target_view = "AgX Punchy"
        # self.oog.target_looks = "Punchy"

        # self.oog.grading.exposure = 1.5
        # self.oog.grading.saturation = 15
        self.oog.grading.contrast = (0.1, 1.0, 1.0)
        # TODO contrast looks broken, find workaround

        self._apply_proc_n_write()
        return

    def test_write_2(self):

        self.oog.input_encoding = "ACES2065-1"
        self.oog.target_display = "sRGB"
        self.oog.target_view = "AgX"
        # self.oog.target_looks = "OverExposed"

        self.oog.grading.offset = 0.3

        self._apply_proc_n_write()
        return


if __name__ == "__main__":
    unittest.main()