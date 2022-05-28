"""

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, List, Union, Literal

import numpy.testing

import lxmImageIO as liio

__all__ = ("BaseTransformtest",)


class BaseTransformtest(ABC):
    """
    Apply color processes on a bunch of RGB images holded in ``imgs`` attribute.
    Define one time the process to apply (``method``) and test it automatically on
    different array image.
    ::

        imgs:       method(**params):              expected
        array --------->|-------> asert equal <--- array
        array --------->|-------> asert equal <--- array
        ...   --------->|-------> asert equal <--- ...

    Must be subclassed with ``unittest.TestCase``

    ``setUp`` and ``tearDown`` must be re-implemented, but you can just call super()
    """

    imgs: liio.containers.DataArrayStack = liio.io.read.readToDataArrayStack(
        (0.5, 0.1, 0.1),
        (0.67, 1.53, 1.456),
        (-0.67, 0.145, 1.456),
    )
    """
    Sample data to perform the test on.
    
    Can be overriden.
    """

    # HACK: wrap the function in a list so when called in class, self is not passed
    method: List[Callable[[numpy.ndarray, ...], numpy.ndarray]] = None
    """
    function to apply on all images from ``imgs`` that then produce the 
    images in ``expected``.
    
    Function expect at least:
    
    - an image as numpy ndarray as first argument
    - return the processed argument image, still as numpy.ndarray
    
    HACK: wrap the function in a list so when called in class, self is not passed
    """

    # All the under MUST be overriden at instance level.
    expected: liio.containers.DataArrayStack = None
    """
    list of images that must assert equal to the ones in ``imgs`` attribute
    """
    params: dict = None
    """
    kwargs to pass to ``method`` attribute
    """
    precision: Union[int, float] = None
    """
    Unit scale depends of the chosen precision_method.
    """
    precision_method: Literal["decimal", "relativeTolerance"] = None
    """
    Which numpy function to use to assert arrays :
    
    -
        decimal : equal up to the number of given decimals (``precision`` attribute)
    - 
        relativeTolerance : equal up to a given tolerance factor. Best for complex 
        operations that might produce imprecisions.
    """

    @abstractmethod
    def setUp(self):

        self.expected = None
        self.params = {}
        self.precision = 4
        self.precision_method = "decimal"

    @abstractmethod
    def tearDown(self):

        img: liio.containers.DataArray
        for i, img in enumerate(self.imgs):

            img: numpy.ndarray = img.array

            with self.subTest(f"{i} - Image {liio.utils.img2str(img)}"):

                result = self.method[0](img, **self.params)
                expected: liio.containers.DataArray = self.expected[i]
                if not expected:
                    self.log(
                        f"Missing expected for index {i}: skipping subtest.",
                        subtestId=i,
                    )
                    continue
                expected: numpy.ndarray = expected.array

                msg = (
                    f"Original={liio.utils.img2str(img)}-{result.shape}\n        "
                    f"Result={liio.utils.img2str(result)}-{result.shape},\n      "
                    f"Expected={liio.utils.img2str(expected)}-{expected.shape}"
                )
                self.log(msg, subtestId=i)

                if self.precision_method == "decimal":
                    numpy.testing.assert_almost_equal(
                        result, expected, self.precision, msg
                    )
                elif self.precision_method == "relativeTolerance":
                    numpy.testing.assert_allclose(
                        result, expected, self.precision, err_msg=msg
                    )
                else:
                    raise TypeError(
                        f"Unsported precision_method {self.precision_method}"
                    )

        self.expected = None
        self.params = None
        self.precision = None
        return

    def log(self, msg: str, subtestId: int = 0):
        out = ""
        if subtestId == 0:
            out += f"{'='*99}\n[{self.id()}]\n"
        out += f"↳ {subtestId} - {msg}\n"
        print(out)
