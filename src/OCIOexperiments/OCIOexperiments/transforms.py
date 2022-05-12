"""

"""
import logging
from typing import Tuple, Union

import numpy

from . import c

logger = logging.getLogger(f"{c.ABR}.transforms")


def open_domain_to_normalized_log2(
    in_od: numpy.ndarray,
    in_midgrey: float = 0.18,
    minimum_ev: float = -10.0,
    maximum_ev: float = +6.5,
) -> numpy.ndarray:
    """
    Similar to lg2 AllocationTransform.
    Source: https://github.com/sobotka/AgX-S2O3/blob/main/AgX.py

    Args:
        in_od: floating point image in open-domain state
        in_midgrey:
        minimum_ev:
        maximum_ev:

    """

    in_od[in_od <= 0.0] = numpy.finfo(float).eps

    output_log = numpy.clip(numpy.log2(in_od / in_midgrey), minimum_ev, maximum_ev)

    total_exposure = maximum_ev - minimum_ev
    return (output_log - minimum_ev) / total_exposure


def saturate(
    array: numpy.ndarray,
    saturation: Union[float, Tuple[float, float, float]],
) -> numpy.ndarray:
    """
    SRC: src/OpenColorIO/ops/gradingprimary/GradingPrimaryOpCPU.cpp#L214

    Args:
        array:
        saturation:
            saturation with different coeff per channel,
            or same value for all channels

    Returns:
        input array with the given saturation value applied
    """

    luma = array * (0.2126, 0.7152, 0.0722)
    luma = numpy.sum(luma, axis=2)
    luma = numpy.stack((luma,) * 3, axis=-1)

    array -= luma
    array *= saturation
    array += luma

    return array


def contrast_linear(
    array: numpy.ndarray,
    contrast: Union[float, Tuple[float, float, float]],
    pivot: float,
) -> numpy.ndarray:
    r"""
    Supports negatives in array to avoid nans.

    SRC: src\OpenColorIO\ops\gradingprimary\GradingPrimaryOpCPU.cpp#L180
    """
    # SRC: src\OpenColorIO\ops\gradingprimary\GradingPrimary.cpp#L194
    pivot_actual = 0.18 * pow(2, pivot)
    pivot_actual = numpy.copysign(pivot_actual, array)
    return numpy.power(abs(array / pivot_actual), contrast) * pivot_actual


def contrast_log(
    array: numpy.ndarray,
    contrast: Union[float, Tuple[float, float, float]],
    pivot: float,
) -> numpy.ndarray:
    r"""
    src\OpenColorIO\ops\gradingprimary\GradingPrimaryOpCPU.cpp#L173
    """
    # src\OpenColorIO\ops\gradingprimary\GradingPrimary.cpp#L151
    pivot_actual = 0.5 + pivot * 0.5
    return (array - pivot_actual) * contrast + pivot_actual
