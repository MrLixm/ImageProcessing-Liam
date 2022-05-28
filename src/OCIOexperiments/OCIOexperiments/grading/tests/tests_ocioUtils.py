import unittest
import PyOpenColorIO as ocio
import numpy
import numpy.testing

import OCIOexperiments as ocex
from OCIOexperiments import testing
from OCIOexperiments.grading import interactive


REMOVE_WRITES = True


def apply_gi_on_img(
    img: numpy.ndarray,
    gi: interactive.GradingInteractive,
    config: ocio.Config,
) -> numpy.ndarray:

    tsfm_gp = ocio.GradingPrimaryTransform(
        gi._grading_primary,
        gi.grading_space,
        True,
    )

    proc: ocio.Processor = config.getProcessor(tsfm_gp)
    proc: ocio.CPUProcessor = proc.getDefaultCPUProcessor()

    out = img.copy()
    proc.applyRGB(out)
    return out


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

        gi = interactive.GradingInteractive()

        gi.saturation = 0.666

        gp = gi._grading_primary
        self.assertEqual(gp.saturation, 0.666)

        return

    def test_properties(self):

        gi = interactive.GradingInteractive()

        self.assertTrue(gi.is_default)

        gi.exposure = 0.5

        self.assertFalse(gi.is_default)
        self.assertFalse(gi.is_modified_sat_only)

        gi = interactive.GradingInteractive()

        gi.saturation = 0.1

        self.assertTrue(gi.is_modified_sat_only)
        self.assertFalse(gi.is_default)

        return

    def test__propconfig(self):

        gi = interactive.GradingInteractive()

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
        self.gi = interactive.GradingInteractive()
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


class TestGradingInteractiveData(testing.BaseTransformtest, unittest.TestCase):

    config = ocio.Config().CreateFromFile(
        str(ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio")
    )

    imgs: testing.DataArrayStack = testing.DataArrayStack(
        (0.5, 0.1, 0.1),
        (0.36, 1.4523, 0.7),
        ocex.c.DATA_DIR / "renders" / "dragonscene_ap0.half.1001.exr",
    )

    method = [apply_gi_on_img]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_expoNsaturate(self):

        gi = interactive.GradingInteractive()
        gi.exposure = -0.5
        gi.saturation = 2.0

        self.params = {"gi": gi, "config": self.config}
        self.expected = self.imgs.apply_op(ocex.transforms.saturate, 2.0)
        self.expected = self.expected.apply_op(ocex.transforms.exposure, -0.5)

        return

    def test_saturate_2x0(self):

        gi = interactive.GradingInteractive()
        gi.saturation = 2.0

        self.params = {"gi": gi, "config": self.config}
        self.expected = self.imgs.apply_op(ocex.transforms.saturate, 2.0)

        return

    def test_saturate_2x0_log(self):

        gi = interactive.GradingInteractive()
        gi.saturation = 2.0
        gi.grading_space = ocio.GRADING_LOG

        self.params = {"gi": gi, "config": self.config}
        self.expected = self.imgs.apply_op(ocex.transforms.saturate, 2.0)

        return


if __name__ == "__main__":
    unittest.main()
