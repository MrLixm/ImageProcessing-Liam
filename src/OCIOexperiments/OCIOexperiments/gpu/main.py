"""

"""
import numpy

import PyOpenColorIO as ocio

__all__ = ("convert_gpu",)


def convert_gpu(
    array: numpy.ndarray,
    config: ocio.Config,
    source: str,
    target: str,
    look: ocioUtils.GradingInteractive,
) -> numpy.ndarray:
    """

    Args:
        look:
        array: image to modify as 32bit float R-G-B numpy array
        config: open color io config to use
        source:
            name of the colorspace the array is encoded in, must exist in the config
        target:
            name of the colorspace to encode the array to, must exist in the config.
            This can be a <colorspace> or a <display>

    Returns:
        color-transformed version of the given <array>.
    """
    pass
