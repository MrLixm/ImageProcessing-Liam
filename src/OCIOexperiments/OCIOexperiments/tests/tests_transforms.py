"""

"""
import unittest

import OCIOexperiments as ocex
from lxmImageIO import testing
from lxmImageIO import io


class TestOpenDomainToNormalizedLog2(unittest.TestCase):
    pass


class TestSaturate(testing.BaseTransformtest, unittest.TestCase):
    """
    Reference Nuke scene :

        set cut_paste_input [stack 0]
    version 13.1 v3
    Constant {
     inputs 0
     color {-0.67 0.145 1.456 1}
     format "256 256 0 0 256 256 1 square_256"
     name Constant3
     selected true
     xpos -132
     ypos -283
    }
    Constant {
     inputs 0
     color {0.67 1.53 1.456 1}
     format "256 256 0 0 256 256 1 square_256"
     name Constant1
     selected true
     xpos -239
     ypos -281
    }
    Constant {
     inputs 0
     color {0.5 0.1 0.1 1}
     format "256 256 0 0 256 256 1 square_256"
     name Constant2
     selected true
     xpos -344
     ypos -280
    }
    Switch {
     inputs 3
     which {{frame}}
     name Switch1
     selected true
     xpos -239
     ypos -173
    }
    Expression {
     temp_name0 L
     temp_expr0 wR*r+wG*g+wB*b
     expr0 L+saturation.r*(r-L)
     expr1 L+saturation.g*(g-L)
     expr2 L+saturation.b*(b-L)
     name ExprSaturation
     selected true
     xpos -239
     ypos -105
     addUserKnob {20 User}
     addUserKnob {6 color_rgba_panelDropped l "panel dropped state" +HIDDEN +STARTLINE}
     addUserKnob {18 saturation}
     saturation 2
     addUserKnob {6 saturation_panelDropped l "panel dropped state" -STARTLINE +HIDDEN}
     addUserKnob {7 wR}
     wR 0.2126
     addUserKnob {7 wG}
     wG 0.7152
     addUserKnob {7 wB}
     wB 0.0722
     addUserKnob {6 color_rgb_panelDropped l "panel dropped state" +HIDDEN +STARTLINE}
    }
    """

    method = [ocex.transforms.saturate]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_0x5(self):

        self.params = {"saturation": 0.5}
        self.expected = io.read.readToDataArrayStack(
            (0.34252, 0.14252, 0.14252),
            (1.00591, 1.43591, 1.39891),
            (-0.30181, 0.10569, 0.76119),
        )

    def test_2x0(self):

        self.params = {"saturation": 2.0}
        self.expected = io.read.readToDataArrayStack(
            (0.81496, 0.01496, 0.01496),
            (-0.00182, 1.71818, 1.57018),
            (-1.40639, 0.22362, 2.84561),
        )


class TestContrastLinear(testing.BaseTransformtest, unittest.TestCase):

    method = [ocex.transforms.contrast_linear]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_0x5_0x18(self):

        self.params = {"contrast": 0.5, "pivot": 0.18}
        self.expected = io.read.readToDataArrayStack(
            (0.31931, 0.14280, 0.14280),
            (0.36963, 0.55857, 0.54489),
            (-0.36963, 0.17195, 0.54489),
        )


class TestOffset(testing.BaseTransformtest, unittest.TestCase):

    method = [ocex.transforms.offset]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_0x5(self):
        offset = 0.5
        self.params = {"o": offset}
        self.expected = io.read.readToDataArrayStack(
            (0.5 + offset, 0.1 + offset, 0.1 + offset),
            (0.67 + offset, 1.53 + offset, 1.456 + offset),
            (-0.67 + offset, 0.145 + offset, 1.456 + offset),
        )

    def test_n0x13(self):
        offset = -0.13
        self.params = {"o": offset}
        self.expected = io.read.readToDataArrayStack(
            (0.5 + offset, 0.1 + offset, 0.1 + offset),
            (0.67 + offset, 1.53 + offset, 1.456 + offset),
            (-0.67 + offset, 0.145 + offset, 1.456 + offset),
        )


class TestClamp(testing.BaseTransformtest, unittest.TestCase):

    method = [ocex.transforms.clamp]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_min0x36_max1x16(self):

        self.params = {"min_out": 0.36, "max_out": 1.16}
        self.expected = io.read.readToDataArrayStack(
            (0.5, 0.36, 0.36),
            (0.67, 1.16, 1.16),
            (0.36, 0.36, 1.16),
        )


if __name__ == "__main__":
    unittest.main()
