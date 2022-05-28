import logging

import numpy

from . import c

__all__ = ("img2str",)

logger = logging.getLogger(f"{c.ABR}.utils")


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
