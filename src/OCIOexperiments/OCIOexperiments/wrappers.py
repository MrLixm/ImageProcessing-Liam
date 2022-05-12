"""

"""
from typing import Union, Tuple

import PyOpenColorIO as ocio

__all__ = ("to_rgbm",)


def to_rgbm(
    value: Union[float, Tuple[float, float, float]],
) -> ocio.GradingRGBM:
    """
    Convert a python object to an OCIO GradingRGBM instance to use for GradingPrimary.

    Args:
        value: a value to apply on all channel or one different per-channel (RGB)

    Returns:
        GradingRGBM instance
    """

    grgbm = ocio.GradingRGBM()
    if isinstance(value, float):
        grgbm.red = 1.0
        grgbm.green = 1.0
        grgbm.blue = 1.0
        grgbm.master = value
    else:
        grgbm.red = value[0]
        grgbm.green = value[1]
        grgbm.blue = value[2]
        grgbm.master = 1.0

    return grgbm
