import logging
from pathlib import Path
from typing import Union, Tuple, NewType, Literal

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


def readToImage(input_path: Path, colorspace=None) -> liio.containers.ImageContainer:

    imgin: oiio.ImageInput = oiio.ImageInput.open(str(input_path))
    assert imgin, f"[readToImage] OIIO: ImageInput for {input_path} not created."
    array: numpy.ndarray = imgin.read_image(oiio.FLOAT)
    imgspec: oiio.ImageSpec = imgin.spec()

    img = liio.containers.ImageContainer(
        array=array,
        width=imgspec.full_width,
        height=imgspec.full_height,
        channels=imgspec.nchannels,
        # TODO better colorspace handling with ocio.ColorSpace
        colorspace=colorspace,
        path=input_path,
    )
    return img


DataArrayTypes = NewType(
    "DataArrayTypes",
    Union[Path, str, Tuple[float, float, float], liio.containers.DataArray],
)


def readToDataArray(data: DataArrayTypes) -> liio.containers.DataArray:
    """
    Convert different type of objects representing an array to a DataArray instance.
    """

    if isinstance(data, (Path, str)):

        array = readToArray(Path(data), method="oiio")

    elif isinstance(data, tuple) and len(data) == 3:

        array = liio.io.create.createConstantImage(data)

    elif isinstance(data, numpy.ndarray):

        array = data

    elif isinstance(data, liio.containers.DataArray):

        return data

    else:
        raise TypeError(f"Unsupported data type {type(data)} passed.")

    return liio.containers.DataArray(array=array)


def readToDataArrayStack(*args: DataArrayTypes) -> liio.containers.DataArrayStack:
    """
    Convert different type of objects (that can become a DataArray) to a DataArray stack
    """
    out = list()
    for arg in args:
        out.append(readToDataArray(arg))
    return liio.containers.DataArrayStack(*out)
