"""

"""
from functools import cache
import logging
import sys
from pathlib import Path
from typing import Literal, List, Union, Any

import numpy
import PyOpenColorIO as ocio

from . import c
from . import io

__all__ = ["run1", "transform_array_1"]

logger = logging.getLogger(f"{c.ABR}.basic")


CONFIG_PATH = Path(r"F:\softwares\color\library\agx\AgXc\v0.1.4\config\config.ocio")


@cache
def get_procs1() -> List[ocio.CPUProcessor]:

    ocioconfig: ocio.Config = ocio.Config().CreateFromFile(str(CONFIG_PATH))

    ocio_processor_1: ocio.Processor = ocioconfig.getProcessor(
        "sRGB",
        "Linear sRGB",
    )

    ocio_display = ocioconfig.getDefaultDisplay()
    ocio_processor_2: ocio.Processor = ocioconfig.getProcessor(
        ocio.ROLE_SCENE_LINEAR,
        ocio_display,
        ocioconfig.getDefaultView(ocio_display),
        ocio.TRANSFORM_DIR_FORWARD,
    )

    ocio_procs: List[ocio.CPUProcessor] = [
        ocio_processor_1.getDefaultCPUProcessor(),
        ocio_processor_2.getDefaultCPUProcessor(),
    ]

    logger.info("[get_procs1] Finished and cached.")
    return ocio_procs


def transform_array_1(array: numpy.ndarray) -> numpy.ndarray:
    """
    - Linearize a sRGB display image,
    - apply basic grading (exposure boost + decrunch)
    - apply the AgX punchy view-transform

    Args:
        array:

    """

    processors = get_procs1()

    # apply linearisation
    processors[0].applyRGB(array)
    array *= 15  # gain 15
    array = numpy.power(array, 1 / 1.15)  # gamma 1.15

    # apply view transform
    processors[1].applyRGB(array)

    return array


def run1():

    export_path = c.OUTPUT_DIR / "ocio_tests.01.tif"
    input1 = c.DATA_DIR / "webcam" / "webcam-c922-A.0001.tif"

    image = io.array_read(
        input_path=input1,
        method="oiio",
    )

    image = transform_array_1(array=image)

    logger.info(f"[run1] Image proccessed. Now as {image.shape} dtype={image.dtype}")

    io.array_write(
        array=image,
        export_path=export_path,
        bitdepth=numpy.float32,
        method="oiio",
    )

    logger.info(f"[run1] Finished.")
    return


if __name__ == "__main__":

    run1()
