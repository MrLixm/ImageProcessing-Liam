import logging
from pathlib import Path
from typing import Literal, List, Union, Any, Tuple

import colour.io
import cv2
import numpy
import OpenImageIO as oiio
import PIL
import PIL.Image

from . import c

__all__ = (
    "img2str",
    "make_constant_image",
    "array_read",
    "array_write",
)

logger = logging.getLogger(f"{c.ABR}.io")


def img2str(img: numpy.ndarray, single_pixel=True) -> str:
    """
    Pretty print a 2D image to a str.

    Args:
        img: 2D image as numpy array
        single_pixel: if True only print the first pixel at x:0,y:0
    """

    if single_pixel:
        img: numpy.ndarray = img[0][0]

    with numpy.printoptions(
        precision=3,
        suppress=True,
        formatter={"float": "{: 0.5f}".format},
    ):
        return f"{img}"


def make_constant_image(
    color: Tuple[float, float, float],
    size: Tuple[int, int] = (4, 4),
) -> numpy.ndarray:
    """
    Create a 32float R-G-B image of the given dimensions filled with
     the given constant color.

    Args:
        color: a color specified as R-G-B
        size: dimensions of the image to create as (width, height)
    """
    return numpy.full(
        (size[0], size[1], 3),
        color,
        dtype=numpy.float32,
    )


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
