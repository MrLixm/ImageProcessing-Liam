import time
import unittest
from functools import partial
from pathlib import Path

import PyOpenColorIO as ocio
import colour.io

import OCIOexperiments as ocex
from OCIOexperiments.gpu import ocioUtils


class TestGradingInteractive(unittest.TestCase):
    def setUp(self):
        self.dynamicprop = None
        self.dynamicprop_value = None
        return

    def tearDown(self):
        self.dynamicprop = None
        self.dynamicprop_value = None
        return

    def test_grading_primary(self):

        gi = ocioUtils.GradingInteractive()

        gi.contrast = 0.666
        gi.lift = 0.666
        gi.offset = 0.666
        gi.pivot = 0.666
        gi.saturation = 0.666

        gp = gi.grading_primary
        self.assertTrue(
            self.rgbm_equal_rgbm(gp.contrast, self.to_rgbm(0.666)), f"{gp.contrast}"
        )
        self.assertTrue(self.rgbm_equal_rgbm(gp.lift, self.to_rgbm(0.666)))
        self.assertTrue(self.rgbm_equal_rgbm(gp.offset, self.to_rgbm(0.666)))
        self.assertFalse(self.rgbm_equal_rgbm(gp.offset, self.to_rgbm(1.8)))
        self.assertEqual(gp.pivot, 0.666)
        self.assertEqual(gp.saturation, 0.666)

        gi.contrast = (0.1, 1, 0.1, 1)
        self.assertFalse(
            self.rgbm_equal_rgbm(gp.contrast, self.to_rgbm((0.1, 1, 0.1, 1))),
            f"gp.contrast = {gp.contrast}",
        )
        gp = gi.grading_primary
        self.assertTrue(
            self.rgbm_equal_rgbm(gp.contrast, self.to_rgbm((0.1, 1, 0.1, 1))),
            f"gp.contrast = {gp.contrast}",
        )

        return

    def test_signals(self):

        gi = ocioUtils.GradingInteractive()
        gi.sgn_dynamicprops.connect(self._signal_receiver)

        gi.exposure = 2.5

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_EXPOSURE)
        self.assertEqual(self.dynamicprop_value, 2.5)

        gi.gamma = 2.2

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_GAMMA)
        self.assertEqual(self.dynamicprop_value, 2.2)

        gi.saturation = 4.6

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY)
        self.assertEqual(self.dynamicprop_value, 4.6)

        gi.grading_space = ocio.GRADING_LIN

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY)
        self.assertEqual(self.dynamicprop_value, ocio.GRADING_LIN)

    def _signal_receiver(self, dynamicprop, value):
        self.dynamicprop = dynamicprop
        self.dynamicprop_value = value
        return

    @staticmethod
    def to_rgbm(v):
        return ocioUtils.to_rgbm_ocio(v)

    @staticmethod
    def rgbm_equal_rgbm(a, b):

        return (
            a.red == b.red
            and a.green == b.green
            and a.blue == b.blue
            and a.master == b.master
        )


class TestOcioOperationGraph(unittest.TestCase):
    def test_init(self):
        # Must not raise anything

        config_path = ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio"
        oog = ocioUtils.OcioOperationGraph(config=config_path)

        config = ocio.Config().CreateFromFile(str(config_path))
        oog = ocioUtils.OcioOperationGraph(config=config_path)

        self.assertRaises(Exception, partial(ocioUtils.OcioOperationGraph, "C:"))

        return


class TestOcioOperationGraphAgx(unittest.TestCase):

    config_path = ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio"

    def setUp(self):
        self.oog = ocioUtils.OcioOperationGraph(config=self.config_path)
        return

    def tearDown(self):
        self.oog = None
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
        self.oog.target_looks = "Punchy"

        self.oog.grading.exposure = 1.5
        self.oog.grading.saturation = 15
        self.oog.grading.contrast = (4.5, 4.1, 1, 1)

        proc = self.oog.get_proc()
        proc: ocio.CPUProcessor = proc.getDefaultCPUProcessor()

        img = ocex.c.DATA_DIR / "renders" / "dragonscene_ap0.half.1001.exr"
        img = colour.io.read_image(str(img))
        print(img.shape)

        proc.applyRGB(img)

        out_path = Path(__file__).parent / "_outputs" / "dragonscene_ap0.half.1002.jpg"
        colour.io.write_image(img, str(out_path))
        self.assertTrue(out_path.exists())
        # out_path.unlink()
        return


if __name__ == "__main__":
    unittest.main()
