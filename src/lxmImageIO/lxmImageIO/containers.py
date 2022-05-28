"""

"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import numpy

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
