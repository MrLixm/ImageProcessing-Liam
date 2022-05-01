"""

"""
import logging

import numpy

from . import c

logger = logging.getLogger(f"{c.ABR}.transforms")


def open_domain_to_normalized_log2(
    in_od: numpy.ndarray,
    in_midgrey: float = 0.18,
    minimum_ev: float = -10.0,
    maximum_ev: float = +6.5,
) -> numpy.ndarray:
    """
    Similar to lg2 AllocationTransform.
    Source: https://github.com/sobotka/AgX-S2O3/blob/main/AgX.py

    Args:
        in_od: numpy array
        in_midgrey:
        minimum_ev:
        maximum_ev:

    """

    in_od[in_od <= 0.0] = numpy.finfo(float).eps

    output_log = numpy.clip(numpy.log2(in_od / in_midgrey), minimum_ev, maximum_ev)

    total_exposure = maximum_ev - minimum_ev
    return (output_log - minimum_ev) / total_exposure
