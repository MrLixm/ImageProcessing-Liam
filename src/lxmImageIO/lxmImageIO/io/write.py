import logging
from pathlib import Path
from typing import Literal, Union, Any

import cv2
import numpy
import OpenImageIO as oiio
import PIL
import PIL.Image

from . import c

__all__ = ("writeToArray",)

logger = logging.getLogger(f"{c.ABR}.write")


def writeToArray(
    array: numpy.ndarray,
    target: Path,
    bitdepth: Union[numpy.float32, numpy.uint16, numpy.uint8],
    method: Literal["oiio", "cv2", "pillow"],
    **kwargs,
):
    """

    Args:
        bitdepth:
        array:
            numpy array: (R-G-B encoded)(float32 type)
        target: full path with extension for export
        method: which librairy to choose for export
        **kwargs: kwargs passed to the writing method for each librairy

    Returns:

    """
    out_image: Any
    assert array.dtype == numpy.float32, (
        f"[array_write] Given array {array.shape} is "
        f"not of type float32 but {array.dtype}"
    )

    if method == "cv2":

        if bitdepth != numpy.float32:
            array *= 255
            array: numpy.ndarray = array.astype(bitdepth)

        array = cv2.cvtColor(
            array,
            cv2.COLOR_RGB2BGR,
        )
        cv2.imwrite(str(target), array, **kwargs)

    elif method == "pillow":

        if bitdepth != numpy.float32:
            array *= 255
            array: numpy.ndarray = array.astype(bitdepth)

        out_image: PIL.Image.Image = PIL.Image.fromarray(array, mode="RGB")
        out_image.save(target, **kwargs)

    elif method == "oiio":

        if bitdepth == numpy.float32:
            _bitdepth = oiio.TypeDesc.TypeFloat
        else:
            _bitdepth = oiio.TypeDesc.TypeInt

        out_image: oiio.ImageOutput = oiio.ImageOutput.create(str(target))
        assert out_image, f"OIIO: ImageOutput for {target} not created."
        spec = oiio.ImageSpec(
            array.shape[1],
            array.shape[0],
            array.shape[2],
            _bitdepth,
        )

        out_image.open(str(target), spec)
        try:
            out_image.write_image(array)
        except:
            raise
        finally:
            out_image.close()

    logger.info(f"[array_write] Array {array.shape} exported to <{target}>.")
    return
