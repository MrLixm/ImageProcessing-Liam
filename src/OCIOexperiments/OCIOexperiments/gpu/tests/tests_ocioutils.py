import unittest

import PyOpenColorIO as ocio
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
        self.assertTrue(self.rgbm_equal_rgbm(gp.contrast, self.to_rgbm(0.666)))
        self.assertTrue(self.rgbm_equal_rgbm(gp.lift, self.to_rgbm(0.666)))
        self.assertTrue(self.rgbm_equal_rgbm(gp.offset, self.to_rgbm(0.666)))
        self.assertFalse(self.rgbm_equal_rgbm(gp.offset, self.to_rgbm(1.8)))
        self.assertEqual(gp.pivot, 0.666)
        self.assertEqual(gp.saturation, 0.666)

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
        rgbm = ocio.GradingRGBM()
        rgbm.master = v
        return rgbm

    @staticmethod
    def rgbm_equal_rgbm(a, b):

        return (
            a.red == b.red
            and a.green == b.green
            and a.blue == b.blue
            and a.master == b.master
        )


if __name__ == "__main__":
    unittest.main()
