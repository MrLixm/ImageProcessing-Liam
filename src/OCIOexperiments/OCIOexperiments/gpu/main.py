"""

"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import numpy

import PyOpenColorIO as ocio

__all__ = (
    "ImageContainer",
    "convert_gpu",
)


@dataclass
class ImageContainer:
    """
    Contains a whole image with important information about it.
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


def convert_gpu(
    array: numpy.ndarray,
    config: ocio.Config,
    source: str,
    target: str,
    look: ocioUtils.GradingInteractive,
) -> numpy.ndarray:
    """

    Args:
        look:
        array: image to modify as 32bit float R-G-B numpy array
        config: open color io config to use
        source:
            name of the colorspace the array is encoded in, must exist in the config
        target:
            name of the colorspace to encode the array to, must exist in the config.
            This can be a <colorspace> or a <display>

    Returns:
        color-transformed version of the given <array>.
    """
    pass
