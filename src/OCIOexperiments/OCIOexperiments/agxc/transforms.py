"""

"""
from functools import cache
import logging
from typing import List

import PyOpenColorIO as ocio
import colour
import numpy

from . import c
from .. import transforms

__all__ = [
    "transform_inout_look_1",
    "transform_native_inout_look_1",
]

logger = logging.getLogger(f"{c.ABR}.transforms")

CONFIG: ocio.Config = ocio.Config().CreateFromFile(str(c.CONFIG_PATH))


agx_compressed_matrix = numpy.asarray(
    [
        [0.84247906, 0.0784336, 0.07922375],
        [0.04232824, 0.87846864, 0.07916613],
        [0.04237565, 0.0784336, 0.87914297],
    ]
)
"""
From https://github.com/sobotka/AgX-S2O3/blob/main/generate_config.py
"""


@cache
def input_srgb_proc() -> ocio.CPUProcessor:
    """
    Convert a sRGB Display image to teh scene reference Linear sRGB.
    """

    proc: ocio.Processor = CONFIG.getProcessor(
        "sRGB",
        "Linear sRGB",
    )
    return proc.getDefaultCPUProcessor()


@cache
def output_srgb_punchy_proc() -> ocio.CPUProcessor:

    ocio_display = CONFIG.getDefaultDisplay()
    proc: ocio.Processor = CONFIG.getProcessor(
        ocio.ROLE_SCENE_LINEAR,
        ocio_display,
        CONFIG.getDefaultView(ocio_display),
        ocio.TRANSFORM_DIR_FORWARD,
    )
    return proc.getDefaultCPUProcessor()


@cache
def get_agx_lut() -> colour.LUT1D:

    lut_path = c.CONFIG_PATH.parent / "LUTs" / "AgX_Default_Contrast.spi1d"

    lut = colour.io.read_LUT_SonySPI1D(str(lut_path))
    return lut


def look_punchy(
    array: numpy.ndarray,
    punchy_gamma: float = 1.3,
    punchy_saturation: float = 1.2,
) -> numpy.ndarray:

    # gamma
    array = array**punchy_gamma
    # saturation based on CDL formula
    # see https://video.stackexchange.com/q/9866
    luma = array * 0.2
    luma = numpy.sum(luma, axis=2)
    luma = numpy.stack((luma,) * 3, axis=-1)
    array -= luma
    array *= punchy_saturation
    array += luma

    return array


def look1(array: numpy.ndarray) -> numpy.ndarray:

    array *= 15  # gain 15
    array = array**1 / 1.15  # gamma 1.15
    return array


def transform_inout_look_1(array: numpy.ndarray) -> numpy.ndarray:
    """
    Using OCIO library.

    - Linearize a sRGB display image,
    - apply basic grading (exposure boost + decrunch)
    - apply the AgX punchy view-transform

    Args:
        array: float32 array, R-G-B format, sRGB Display encoding

    """

    # 1. apply inverse EOTF to linearize
    array: numpy.ndarray = array**2.2

    # grading
    array = look1(array=array)

    # apply view transform
    output_srgb_punchy_proc().applyRGB(array)

    return array


def transform_native_inout_look_1(array: numpy.ndarray) -> numpy.ndarray:
    """
    Using native python function and numpy.

    - Linearize a sRGB display image,
    - apply basic grading (exposure boost + decrunch)
    - apply the AgX punchy view-transform

    Args:
        array: float32 array, R-G-B format, sRGB Display encoding

    """

    # 1. apply inverse EOTF to linearize
    array: numpy.ndarray = array**2.2

    # 2. Apply Grading
    array = look1(array)

    # 3. Apply AgX Log encoding
    array = array.clip(min=0)
    array = colour.algebra.vector_dot(
        agx_compressed_matrix,
        array,
    )
    logarray = transforms.open_domain_to_normalized_log2(
        array,
        minimum_ev=-10.0,
        maximum_ev=6.5,
    )
    logarray = logarray.clip(0.0, 1.0)
    # 4. Apply AgX Base
    array = get_agx_lut().apply(logarray)

    # 5. Apply Punchy Look
    array = look_punchy(array=array)

    # EOTF is already applied
    return array
