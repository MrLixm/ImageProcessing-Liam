"""

"""
from __future__ import annotations
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Callable, Union, Tuple, NewType, Optional, List

import numpy
import numpy.testing
import lxmImageIO as liio
import PyOpenColorIO as ocio

from . import c

__all__ = (
    "ImageContainer",
    "DataArray",
    "DataArrayStack",
)


logger = logging.getLogger(f"{c.ABR}.containers")


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
    colorspace: Optional[ocio.ColorSpace]
    """
    Colorspace the pixel array is encoded in.
    """
    path: Optional[Path]
    """
    File path from where this image was stored. None if generated from scratch.
    """

    def __repr__(self):
        return (
            f"ImageContainer ({self.width}*{self.height})*{self.channels}"
            f" | array[{self.array.dtype}] | with path={self.path}"
        )


class DataArray:
    def __init__(self, array: numpy.ndarray):
        """
        Low-level entity representing an arbitrary data as a numpy array.
        (even if for now these are images).

        Can be build from different object type that will be automatically converted
        internally to an array.

        Args:
            array:
        """

        self._data: numpy.ndarray = None
        self.array = array
        return

    @property
    def array(self, copy=True) -> numpy.ndarray:
        return self.get_array()

    @array.setter
    def array(self, data_value: numpy.ndarray):
        self._data = data_value

    def get_array(self, copy=True):
        """
        Args:
            copy: True to return a copy of the array
        """
        return self._data.copy() if copy else self._data


class DataArrayStack(list):
    def __init__(self, *args: Union[DataArray, numpy.ndarray, Optional]):
        """
        A groups of DataArray as a list.
        Used to batch-apply a similar process to them.

        Some objects holded can be None.

        Args:
            *args: Union[DataArray, None] or Union[numpy.ndarray, None]
        """
        if all(isinstance(arg, DataArray) or arg is None for arg in args):
            super().__init__(args)
        else:
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
        Apply the given ``op`` function to all the holded DataArray.
        This op function must expect:

        - an image as numpy ndarray as first argument
        - return the processed argument image, still as numpy.ndarray

        Args:
            op: function to call on each array holded
            *args: args to pass to the op
            **kwargs: kwargs to pass to the op

        Returns:
            a new version of the DataArrayStack with the op applied
        """

        out: List[numpy.ndarray] = list()
        data: DataArray
        for data in self.__iter__():
            out.append(op(data.array, *args, **kwargs))

        return DataArrayStack(*out)
