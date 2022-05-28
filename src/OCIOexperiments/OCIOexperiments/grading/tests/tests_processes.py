import unittest
from functools import partial
from pathlib import Path

import PyOpenColorIO as ocio
import colour.io
import numpy.testing

import OCIOexperiments as ocex
from OCIOexperiments import testing
from OCIOexperiments.grading import processes


REMOVE_WRITES = True

RENDER_TEST_1 = Path("./data/test.oog_agx.test_1.ref.tif")


class TestOcioOperationGraph(unittest.TestCase):
    def test_init(self):
        # Must not raise anything

        config_path = ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio"
        oog = processes.OcioOperationGraph(config=config_path)

        config = ocio.Config().CreateFromFile(str(config_path))
        oog = processes.OcioOperationGraph(config=config_path)

        self.assertRaises(Exception, partial(processes.OcioOperationGraph, "C:"))

        return


def apply_proc(
    img: numpy.ndarray, oog: processes.OcioOperationGraph, config: ocio.Config
):

    proc = oog.get_proc()
    proc: ocio.CPUProcessor = proc.getDefaultCPUProcessor()

    out = img.copy()
    proc.applyRGB(out)
    return out


class TestOcioOperationGraphSimple(unittest.TestCase):
    """
    Mostly to chekc it doesn't raise error
    """

    config = ocio.Config().CreateFromFile(
        str(ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio")
    )

    def test_proc1(self):
        oog = processes.OcioOperationGraph(self.config)
        self.assertRaises(AssertionError, oog.get_proc)

        oog.input_encoding = "sRGB"
        oog.target_display = "sRGB"
        # self.oog.target_view = "AgX"

        self.assertRaises(AssertionError, oog.get_proc)

        return

    def test_proc2(self):
        oog = processes.OcioOperationGraph(self.config)

        oog.input_encoding = "sRGB"
        oog.target_display = "sRGB"
        oog.target_view = "BABABOEI"

        self.assertRaises(AssertionError, oog.get_proc)

        return

    def test_proc3(self):
        oog = processes.OcioOperationGraph(self.config)

        oog.input_encoding = "Linear sRGB"
        oog.target_display = "sRGB"
        oog.target_view = "AgX"
        oog.target_looks = "Punchy"

        oog.grading.exposure = 0.5
        oog.grading.saturation = 1.2

        oog.get_proc()

        return


class TestOcioOperationGraphAgx(testing.BaseTransformtest, unittest.TestCase):

    config = ocio.Config().CreateFromFile(
        str(ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio")
    )

    imgs: testing.DataArrayStack = testing.DataArrayStack(
        (0.5, 0.1, 0.1),
        (0.36, 1.4523, 0.7),
        ocex.c.DATA_DIR / "renders" / "dragonscene_ap0.half.1001.exr",
    )

    method = [apply_proc]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_1(self):

        self.precision = 0.05
        self.precision_method = "relativeTolerance"

        oog = processes.OcioOperationGraph(self.config)

        oog.input_encoding = "ACES2065-1"
        oog.target_display = "sRGB"
        oog.target_view = "AgX Punchy"
        # oog.target_looks = "Punchy"

        oog.grading.exposure = 1.5
        oog.grading.saturation = 15

        self.params = {"oog": oog, "config": self.config}
        # all generated through nuke
        self.expected = testing.DataArrayStack(
            testing.DataArray((1.02972, 0.80339, 0.80359)),
            testing.DataArray((0.85478, 1.00726, 0.85478)),
            testing.DataArray(RENDER_TEST_1),
        )
        return

    def test_2(self):

        oog = processes.OcioOperationGraph(self.config)

        oog.input_encoding = "ACES2065-1"
        oog.target_display = "sRGB"
        oog.target_view = "AgX"
        oog.target_looks = "OverExposed"

        self.params = {"oog": oog, "config": self.config}
        # all generated through nuke
        self.expected = testing.DataArrayStack(
            testing.DataArray((0.90552, 0.47522, 0.62818)),
            testing.DataArray((0.68929, 0.94798, 0.8691)),
            None,  # we skip the render for this one
        )
        return


if __name__ == "__main__":
    unittest.main()
