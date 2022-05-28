"""

"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Union, Tuple, NewType, Literal, Optional

import numpy
import numpy.testing

import lxmImageIO as liio
import PyOpenColorIO as ocio

__all__ = ("ImageContainer",)


@dataclass
class ImageContainer:
    """
    Contains a whole image with essential information about it.
    """

    array: numpy.ndarray
    """
    numpy arrays of pixels
    """
    width: float
    height: float
    channels: int
    """
    Number of channels the array has.
    """
    colorspace: ocio.ColorSpace
    """
    Colorspace the pixel array is encoded in.
    """
    path: Optional[Path]
    """
    File path from where this image was stored.
    """

    def __repr__(self):
        return (
            f"ImageContainer ({self.width}*{self.height})*{self.channels}"
            f" | array[{self.array.dtype}] | with path={self.path}"
        )


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

            self.array = liio.io.array_read(Path(data), method="colour")

        elif isinstance(data, tuple) and len(data) == 3:

            self.array = liio.io.make_constant_image(data)

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
