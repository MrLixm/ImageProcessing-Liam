"""

"""
import unittest
from abc import ABC, abstractmethod
from typing import Callable, List

import numpy.testing

import OCIOexperiments as ocex


def img2str(img: numpy.ndarray) -> str:

    img: numpy.ndarray = img[0][0]

    with numpy.printoptions(
        precision=3,
        suppress=True,
        formatter={"float": "{: 0.5f}".format},
    ):
        return f"{img}"


class BaseTransformtest(ABC):

    colors = (
        (0.5, 0.1, 0.1),
        (0.67, 1.53, 1.456),
        (-0.67, 0.145, 1.456),
    )

    # HACK: wrap the function in a list so when called in class, self is not passed
    method: List[Callable[[numpy.ndarray, ...], numpy.ndarray]] = None

    @abstractmethod
    def setUp(self):

        self.imgs = map(ocex.io.make_constant_image, self.colors)
        self.expected: tuple = None
        self.params: dict = {}
        "kwargs to pass to self.method"
        self.precison: int = 4

    @abstractmethod
    def tearDown(self):

        for i, img in enumerate(self.imgs):

            with self.subTest(f"{i} - Image {img2str(img)}"):

                result = self.method[0](img, **self.params)
                expected = ocex.io.make_constant_image(self.expected[i])

                msg = f"Result={img2str(result)}, Expected={img2str(expected)}"
                self._log(msg, subtestId=i)
                numpy.testing.assert_almost_equal(result, expected, self.precison, msg)

        self.imgs = None
        self.expected = None
        self.params = None
        self.precison = None
        return

    def _log(self, msg: str, subtestId: int = 0):
        out = ""
        if subtestId == 0:
            out += f"{'='*99}\n[{self.id()}]\n"
        out += f"↳ {subtestId} - {msg}\n"
        print(out)


class TestOpenDomainToNormalizedLog2(unittest.TestCase):
    pass


class TestSaturate(BaseTransformtest, unittest.TestCase):
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
        self.expected = (
            (0.34252, 0.14252, 0.14252),
            (1.00591, 1.43591, 1.39891),
            (-0.30181, 0.10569, 0.76119),
        )

    def test_2x0(self):

        self.params = {"saturation": 2.0}
        self.expected = (
            (0.81496, 0.01496, 0.01496),
            (-0.00182, 1.71818, 1.57018),
            (-1.40639, 0.22362, 2.84561),
        )


class TestContrastLinear(BaseTransformtest, unittest.TestCase):

    method = [ocex.transforms.contrast_linear]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_0x5_0x18(self):

        self.params = {"contrast": 0.5, "pivot": 0.18}
        self.expected = (
            (0.31931, 0.14280, 0.14280),
            (0.36963, 0.55857, 0.54489),
            (-0.36963, 0.17195, 0.54489),
        )


if __name__ == "__main__":
    unittest.main()
