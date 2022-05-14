import unittest
from functools import partial
from pathlib import Path
from typing import Tuple

import PyOpenColorIO as ocio
import colour.io
import numpy
import numpy.testing

import OCIOexperiments as ocex
from OCIOexperiments import testing
from OCIOexperiments.gpu import ocioUtils
from OCIOexperiments.io import img2str


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
            self.rgbm_equal_rgbm(gp.contrast, self.to_rgbm(0.666, "*")),
            f"{gp.contrast}",
        )
        self.assertTrue(self.rgbm_equal_rgbm(gp.lift, self.to_rgbm(0.666, "+")))
        self.assertTrue(self.rgbm_equal_rgbm(gp.offset, self.to_rgbm(0.666, "+")))
        self.assertFalse(self.rgbm_equal_rgbm(gp.offset, self.to_rgbm(1.8, "+")))
        self.assertEqual(gp.pivot, 0.666)
        self.assertEqual(gp.saturation, 0.666)

        gi.contrast = (0.1, 1, 0.1, 1)
        self.assertFalse(
            self.rgbm_almostequal_rgbm(
                gp.contrast, self.to_rgbm((0.1, 1, 0.1, 1), "*")
            ),
            f"gp.contrast = {gp.contrast}",
        )
        gp = gi.grading_primary
        self.assertTrue(
            self.rgbm_almostequal_rgbm(
                gp.contrast, self.to_rgbm((0.1, 1, 0.1, 1), "*")
            ),
            f"gp.contrast = {gp.contrast}",
        )

        return

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

    @staticmethod
    def to_rgbm(v, m):
        return ocex.wrappers.to_rgbm(v, m)

    @staticmethod
    def rgbm_equal_rgbm(a: ocio.GradingRGBM, b: ocio.GradingRGBM) -> bool:
        return (
            a.red == b.red
            and a.green == b.green
            and a.blue == b.blue
            and a.master == b.master
        )

    @staticmethod
    def rgbm_almostequal_rgbm(a: ocio.GradingRGBM, b: ocio.GradingRGBM) -> bool:
        return (
            bool(numpy.isclose(a.red, b.red))
            and bool(numpy.isclose(a.green, b.green))
            and bool(numpy.isclose(a.blue, b.blue))
            and bool(numpy.isclose(a.master, b.master))
        )


class TestGradingInteractiveSignals(unittest.TestCase):
    def setUp(self):
        self.gi = ocioUtils.GradingInteractive()
        self.dynamicprop = None
        self.dynamicprop_value = None
        return

    def tearDown(self):
        self.gi = None
        self.dynamicprop = None
        self.dynamicprop_value = None
        return

    def test_signals(self):

        self.gi.sgn_dynamicprops.connect(self._signal_receiver)

        self.gi.exposure = 2.5

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_EXPOSURE)
        self.assertEqual(self.dynamicprop_value, 2.5)

        self.gi.gamma = 2.2

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_GAMMA)
        self.assertEqual(self.dynamicprop_value, 2.2)

        self.gi.saturation = 4.6

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY)
        self.assertEqual(self.dynamicprop_value, 4.6)

        self.gi.grading_space = ocio.GRADING_LIN

        self.assertEqual(self.dynamicprop, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY)
        self.assertEqual(self.dynamicprop_value, ocio.GRADING_LIN)

    def _signal_receiver(self, dynamicprop, value):
        self.dynamicprop = dynamicprop
        self.dynamicprop_value = value
        return


class TestGradingInteractiveData(unittest.TestCase):

    config_path = ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio"
    out_dir = Path(__file__).parent / "_outputs"
    render1 = ocex.c.DATA_DIR / "renders" / "dragonscene_ap0.half.1001.exr"

    imgs: testing.DataArrayStack = testing.DataArrayStack(
        (0.5, 0.1, 0.1),
        (0.36, 1.4523, 0.7),
        render1,
    )

    def setUp(self):

        self._config: ocio.Config = ocio.Config().CreateFromFile(str(self.config_path))

        self.gi = ocioUtils.GradingInteractive()
        self.expected: testing.DataArrayStack = None
        self.precision = 4
        return

    def tearDown(self):

        img: testing.DataArray
        for i, img in enumerate(self.imgs):

            img: numpy.ndarray = img.array

            with self.subTest(f"{i} - Image {img2str(img)}"):

                result = self._apply_gi_on_img(img)
                expected: testing.DataArray = self.expected[i]
                expected: numpy.ndarray = expected.array

                msg = (
                    f"Original={img2str(img)}-{result.shape}\n        "
                    f"Result={img2str(result)}-{result.shape},\n      "
                    f"Expected={img2str(expected)}-{expected.shape}"
                )
                self.log(msg, subtestId=i)
                numpy.testing.assert_almost_equal(result, expected, self.precision, msg)

        self._config = None
        self.gi = None
        self.expected = None
        return

    def log(self, msg: str, subtestId: int = 0):
        out = ""
        if subtestId == 0:
            out += f"{'='*99}\n[{self.id()}]\n"
        out += f"↳ {subtestId} - {msg}\n"
        print(out)

    def _apply_gi_on_img(self, img: numpy.ndarray) -> numpy.ndarray:

        tsfm_gp = ocio.GradingPrimaryTransform(
            self.gi.grading_primary,
            self.gi.grading_space,
            True,
        )

        proc: ocio.Processor = self._config.getProcessor(tsfm_gp)
        proc: ocio.CPUProcessor = proc.getDefaultCPUProcessor()

        out = img.copy()
        proc.applyRGB(out)
        return out

    def test_expoNsaturate(self):

        self.gi.exposure = -0.5
        self.gi.saturation = 2.0

        self.expected = self.imgs.apply_op(ocex.transforms.saturate, 2.0)
        self.expected = self.expected.apply_op(ocex.transforms.exposure, -0.5)

        return

    def test_saturate_2x0(self):

        self.gi.saturation = 2.0
        print(self.gi.grading_primary)
        self.expected = self.imgs.apply_op(ocex.transforms.saturate, 2.0)

        return

    def test_saturate_2x0_log(self):

        self.gi.saturation = 2.0
        self.gi.grading_space = ocio.GRADING_LOG
        print(self.gi.grading_primary)
        self.expected = self.imgs.apply_op(ocex.transforms.saturate, 2.0)

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
