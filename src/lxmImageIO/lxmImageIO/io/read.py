import logging
from pathlib import Path
from typing import Union, Tuple, NewType, Literal, Optional

import colour.io
import cv2
import numpy
import OpenImageIO as oiio
import PIL
import PIL.Image

from . import c
import lxmImageIO as liio

__all__ = (
    "readToArray",
    "readToImage",
    "readToDataArray",
)

logger = logging.getLogger(f"{c.ABR}.read")


def readToArray(
    source: Path,
    method: Literal["oiio", "cv2", "pillow", "colour"],
    **kwargs,
) -> numpy.ndarray:
    """

    Args:
        source: full path with extension for input reading
        method: which librairy to choose for export
        **kwargs: kwargs passed to the writing method for each librairy

    Returns:
        32-bit float numpy array of the image
    """
    array: numpy.ndarray

    if method == "cv2":

        array: numpy.ndarray = cv2.imread(str(source), **kwargs)
        array = cv2.cvtColor(
            array,
            cv2.COLOR_BGR2RGB,
        )
        if array.dtype != numpy.float32:
            array = array.astype(numpy.float32)
            array /= 255
            logger.debug("[array_read]<cv2> converted to float32")

    elif method == "pillow":

        array: PIL.Image.Image = PIL.Image.open(source, **kwargs)
        array: numpy.ndarray = array.__array__(dtype=numpy.float32)

    elif method == "oiio":

        array: oiio.ImageInput = oiio.ImageInput.open(str(source), **kwargs)
        assert array, f"OIIO: ImageInput for {source} not created."
        array: numpy.ndarray = array.read_image(oiio.FLOAT)

    elif method == "colour":

        array: numpy.ndarray = colour.io.read_image(
            str(source),
            bit_depth="float32",
            **kwargs,
        )

    else:
        raise ValueError(f"Method <{method}> passed is not supported.")

    logger.info(f"[array_read] Array {array.shape}|{array.dtype} found in <{source}>.")
    return array


def readToImage(
    source: Path,
    colorspace: Optional[str] = None,
) -> liio.containers.ImageContainer:

    imgin: oiio.ImageInput = oiio.ImageInput.open(str(source))
    assert imgin, f"[readToImage] OIIO: ImageInput for {source} not created."
    array: numpy.ndarray = imgin.read_image(oiio.FLOAT)
    imgspec: oiio.ImageSpec = imgin.spec()

    img = liio.containers.ImageContainer(
        array=array,
        width=imgspec.full_width,
        height=imgspec.full_height,
        channels=imgspec.nchannels,
        # TODO better colorspace handling with ocio.ColorSpace
        colorspace=colorspace,
        path=source,
    )
    return img


DataArrayTypes = NewType(
    "DataArrayTypes",
    Union[Path, str, Tuple[float, float, float], liio.containers.DataArray],
)


def readToDataArray(source: DataArrayTypes) -> liio.containers.DataArray:
    """
    Convert different type of objects representing an array to a DataArray instance.
    """

    if isinstance(source, (Path, str)):

        array = readToArray(Path(source), method="oiio")

    elif isinstance(source, tuple) and len(source) == 3:

        array = liio.io.create.createConstantImage(source)

    elif isinstance(source, numpy.ndarray):

        array = source

    elif isinstance(source, liio.containers.DataArray):

        return source

    else:
        raise TypeError(f"Unsupported data type {type(source)} passed.")

    return liio.containers.DataArray(array=array)


def readToDataArrayStack(*args: DataArrayTypes) -> liio.containers.DataArrayStack:
    """
    Convert different type of objects (that can become a DataArray) to a DataArray stack
    """
    out = list()
    for arg in args:
        out.append(readToDataArray(arg))
    return liio.containers.DataArrayStack(*out)
