import unittest
from functools import partial
from pathlib import Path

import PyOpenColorIO as ocio
import colour.io
import numpy
import numpy.testing

import OCIOexperiments as ocex
from OCIOexperiments.gpu import ocioUtils


REMOVE_WRITES = True


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
            self.rgbm_equal_rgbm(gp.contrast, self.to_rgbm(0.666)),
            f"{gp.contrast}",
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

    def test_properties(self):

        gi = ocioUtils.GradingInteractive()

        self.assertTrue(gi.is_default)

        gi.exposure = 0.5

        self.assertFalse(gi.is_default)
        self.assertFalse(gi.is_modified_sat_only)

        gi = ocioUtils.GradingInteractive()

        gi.saturation = 0.1

        self.assertTrue(gi.is_modified_sat_only)
        self.assertFalse(gi.is_default)

        return

    def test__propconfig(self):

        gi = ocioUtils.GradingInteractive()

        self.assertTrue(gi._propconfig.get("exposure")[0] == 0.0)

        gi.exposure = 0.5

        self.assertTrue(gi._propconfig.get("exposure")[0] == 0.0)
        self.assertTrue(
            gi._propconfig.get("exposure")[1] == ocio.DYNAMIC_PROPERTY_EXPOSURE
        )

        gi.saturation = 3.3

        self.assertTrue(gi._propconfig.get("saturation")[0] == 1.0)

        return

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


class TestGradingInteractiveData(unittest.TestCase):

    config_path = ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio"
    out_dir = Path(__file__).parent / "_outputs"

    def setUp(self) -> None:

        self.config: ocio.Config = ocio.Config().CreateFromFile(str(self.config_path))

        img = ocex.c.DATA_DIR / "renders" / "dragonscene_ap0.half.1001.exr"
        self.img_render = colour.io.read_image(str(img))
        print(f"Read <dragonscene_ap0.half.1001.exr>: {self.img_render.shape}")

        self.img_red = ocex.io.make_constant_image((0.5, 0.1, 0.1))

        self.gi = ocioUtils.GradingInteractive()
        return

    def tearDown(self) -> None:
        self.config = None
        self.img_red = None
        self.img_render = None
        self.gi = None
        return

    def _apply_gi_on_img(self, img: numpy.ndarray):

        tsfm_gp = ocio.GradingPrimaryTransform(
            self.gi.grading_primary,
            self.gi.grading_space,
            True,
        )

        proc: ocio.Processor = self.config.getProcessor(tsfm_gp)
        proc: ocio.CPUProcessor = proc.getDefaultCPUProcessor()

        proc.applyRGB(img)
        return

    def test_write_render_1(self):

        img = self.img_render

        self.gi.exposure = -0.5
        self.gi.saturation = 2.0

        self._apply_gi_on_img(img)

        out_path = self.out_dir / f"dragonscene.{self.id()}.jpg"
        colour.io.write_image(img, str(out_path))
        self.assertTrue(out_path.exists())

        if REMOVE_WRITES:
            out_path.unlink()

        return

    def test_img_red_sat_1(self):

        img = self.img_red
        s = 2.0

        self.gi.saturation = s

        self._apply_gi_on_img(img)

        expected = ocex.transforms.saturate(img, s)
        numpy.testing.assert_almost_equal(
            img,
            expected,
            4,
            f"Got {img[1][1]} but expected {expected[1][1]}",
        )

        return

    def test_img_red_sat_log(self):

        img = self.img_red

        self.gi.saturation = 2.0
        self.gi.grading_space = ocio.GRADING_LOG

        self._apply_gi_on_img(img)

        print(img[1][1])
        expected = ocex.io.make_constant_image((0.815, 0.015, 0.015))
        numpy.testing.assert_almost_equal(
            img,
            expected,
            4,
            f"Got {img[1][1]} but expected {expected[1][1]}",
        )

        return


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
