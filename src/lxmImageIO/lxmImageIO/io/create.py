import logging
from typing import Tuple

import numpy

from . import c

__all__ = ("make_constant_image",)

logger = logging.getLogger(f"{c.ABR}.io")


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
