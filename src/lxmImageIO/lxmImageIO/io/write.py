import logging
from pathlib import Path
from typing import Literal, Union, Any

import cv2
import numpy
import OpenImageIO as oiio
import PIL
import PIL.Image

from . import c

__all__ = ("array_write",)

logger = logging.getLogger(f"{c.ABR}.io")


def array_write(
    array: numpy.ndarray,
    export_path: Path,
    bitdepth: Union[numpy.float32, numpy.uint16, numpy.uint8],
    method: Literal["oiio", "cv2", "pillow"],
    **kwargs,
):
    """

    Args:
        bitdepth:
        array:
            numpy array: (R-G-B encoded)(float32 type)
        export_path: full path with extension for export
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
        cv2.imwrite(str(export_path), array, **kwargs)

    elif method == "pillow":

        if bitdepth != numpy.float32:
            array *= 255
            array: numpy.ndarray = array.astype(bitdepth)

        out_image: PIL.Image.Image = PIL.Image.fromarray(array, mode="RGB")
        out_image.save(export_path, **kwargs)

    elif method == "oiio":

        if bitdepth == numpy.float32:
            _bitdepth = oiio.TypeDesc.TypeFloat
        else:
            _bitdepth = oiio.TypeDesc.TypeInt

        out_image: oiio.ImageOutput = oiio.ImageOutput.create(str(export_path))
        assert out_image, f"OIIO: ImageOutput for {export_path} not created."
        spec = oiio.ImageSpec(
            array.shape[1],
            array.shape[0],
            array.shape[2],
            _bitdepth,
        )

        out_image.open(str(export_path), spec)
        try:
            out_image.write_image(array)
        except:
            raise
        finally:
            out_image.close()

    logger.info(f"[array_write] Array {array.shape} exported to <{export_path}>.")
    return
