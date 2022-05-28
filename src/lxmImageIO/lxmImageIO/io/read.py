import logging
from pathlib import Path
from typing import Literal

import colour.io
import cv2
import numpy
import OpenImageIO as oiio
import PIL
import PIL.Image

from . import c

__all__ = ("array_read",)

logger = logging.getLogger(f"{c.ABR}.io")


def array_read(
    input_path: Path,
    method: Literal["oiio", "cv2", "pillow", "colour"],
    **kwargs,
) -> numpy.ndarray:
    """

    Args:
        input_path: full path with extension for input reading
        method: which librairy to choose for export
        **kwargs: kwargs passed to the writing method for each librairy

    Returns:
        32-bit float numpy array of the image
    """
    array: numpy.ndarray

    if method == "cv2":

        array: numpy.ndarray = cv2.imread(str(input_path), **kwargs)
        array = cv2.cvtColor(
            array,
            cv2.COLOR_BGR2RGB,
        )
        if array.dtype != numpy.float32:
            array = array.astype(numpy.float32)
            array /= 255
            logger.debug("[array_read]<cv2> converted to float32")

    elif method == "pillow":

        array: PIL.Image.Image = PIL.Image.open(input_path, **kwargs)
        array: numpy.ndarray = array.__array__(dtype=numpy.float32)

    elif method == "oiio":

        array: oiio.ImageInput = oiio.ImageInput.open(str(input_path), **kwargs)
        assert array, f"OIIO: ImageInput for {input_path} not created."
        array: numpy.ndarray = array.read_image(oiio.FLOAT)

    elif method == "colour":

        array: numpy.ndarray = colour.io.read_image(
            str(input_path),
            bit_depth="float32",
            **kwargs,
        )

    else:
        raise ValueError(f"Method <{method}> passed is not supported.")

    logger.info(
        f"[array_read] Array {array.shape}|{array.dtype} found in <{input_path}>."
    )
    return array
