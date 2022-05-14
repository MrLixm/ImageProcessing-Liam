"""

"""
from typing import Union, Tuple, Literal

import PyOpenColorIO as ocio

__all__ = ("to_rgbm",)


def to_rgbm(
    value: Union[float, Tuple[float, float, float]],
    ocio_math: Literal["*", "+"] = "*",
) -> ocio.GradingRGBM:
    r"""
    Convert a python object to an OCIO GradingRGBM instance to use for GradingPrimary.

    Args:
        ocio_math:
            how OCIO internally applies the master on the R-G-B components, check:
            `src\OpenColorIO\ops\gradingprimary\GradingPrimary.cpp`
        value: a value to apply on all channel or one different per-channel (RGB)

    Returns:
        GradingRGBM instance
    """
    if ocio_math == "*":
        x = 1
    else:
        x = 0

    grgbm = ocio.GradingRGBM()
    if isinstance(value, float):
        grgbm.red = value
        grgbm.green = value
        grgbm.blue = value
        grgbm.master = x
    else:
        grgbm.red = value[0]
        grgbm.green = value[1]
        grgbm.blue = value[2]
        grgbm.master = x

    return grgbm
