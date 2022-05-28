"""

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, List, Union, Tuple, NewType, Literal

import numpy.testing

import OCIOexperiments as ocex
from OCIOexperiments.io import img2str

__all__ = ("DataArray", "BaseTransformtest", "DataArrayStack")


class DataArray:
    pass


DataType = NewType("DataType", Union[Path, str, Tuple[float, float, float], DataArray])


class DataArray:
    def __init__(self, data: DataType):
        """
        Low-level entity representing an arbitrary data as a numpy array.
        (even if for now these are images).

        Data argument can be different type that will be automatically converted
        internally to an array.

        Args:
            data: source to build the array from
        """

        self._data: numpy.ndarray = None

        if isinstance(data, (Path, str)):

            self.array = ocex.io.array_read(Path(data), method="colour")

        elif isinstance(data, tuple) and len(data) == 3:

            self.array = ocex.io.make_constant_image(data)

        elif isinstance(data, numpy.ndarray):

            self.array = data

        elif isinstance(data, DataArray):

            self.array = data.array

        else:
            raise TypeError(f"Unsupported data type {type(data)} passed.")

        return

    @property
    def array(self) -> numpy.ndarray:
        return self._data.copy()

    @array.setter
    def array(self, data_value: numpy.ndarray):
        self._data = data_value


class DataArrayStack(list):
    def __init__(self, *args: DataType):
        """
        A groups of DataArray to batch-apply similar process.

        Args:
            *args: type supported are defined by DataArray
        """
        out = [DataArray(arg) if arg is not None else None for arg in args]
        super().__init__(out)
        return

    def apply_op(
        self,
        op: Callable[[numpy.ndarray, ...], numpy.ndarray],
        *args,
        **kwargs,
    ) -> DataArrayStack:
        """

        Args:
            op: function to call on each array holded
            *args: args to pass to the op
            **kwargs: kwargs to pass to the op

        Returns:
            a new version of the DataArrayStack with the op applied
        """

        out = list()
        for data in self.__iter__():
            out.append(op(data.array, *args, **kwargs))

        return DataArrayStack(*out)


class BaseTransformtest(ABC):
    """
    Apply color processes on a bunch of RGB images holded in imgs.
    Define one time the process to apply and test it automatically on different array
    image.

    Must be subclassed with unittest.case.

    setUp and tearDown must be re-implemented, but you can just call super()
    """

    imgs: DataArrayStack = DataArrayStack(
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

    # All the under MUST be overriden at instance level.
    expected: DataArrayStack = None
    params: dict = None
    """
    kwargs to pass to self.method
    """
    precision: Union[int, float] = None
    """
    Unit scale depends of the chosen precision_method.
    """
    precision_method: Literal["decimal", "relativeTolerance"] = None

    @abstractmethod
    def setUp(self):

        self.expected = None
        self.params = {}
        self.precision = 4
        self.precision_method = "decimal"

    @abstractmethod
    def tearDown(self):

        img: DataArray
        for i, img in enumerate(self.imgs):

            img: numpy.ndarray = img.array

            with self.subTest(f"{i} - Image {img2str(img)}"):

                result = self.method[0](img, **self.params)
                expected: DataArray = self.expected[i]
                if not expected:
                    self.log(
                        f"Missing expected for index {i}: skipping subtest.",
                        subtestId=i,
                    )
                    continue
                expected: numpy.ndarray = expected.array

                msg = (
                    f"Original={img2str(img)}-{result.shape}\n        "
                    f"Result={img2str(result)}-{result.shape},\n      "
                    f"Expected={img2str(expected)}-{expected.shape}"
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
