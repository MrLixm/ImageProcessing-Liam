"""

"""
from dataclasses import dataclass
from typing import Literal, Optional

import numpy

import PyOpenColorIO as ocio

__all__ = ["InteractiveLook", "convert_gpu"]


@dataclass
class InteractiveLook:
    exposure: float = 1.0
    gamma: float = 1.0
    contrast: float = 0.0
    pivot: float = 0.18
    saturation: float = 1.0


def convert_gpu(
    array: numpy.ndarray,
    config: ocio.Config,
    source: str,
    target: str,
    look: InteractiveLook,
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
