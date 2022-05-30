"""

"""
import logging
import sys

import PyOpenColorIO as ocio

import lxmImageIO as liio
import pixelDataTesting as pxdt
import OCIOexperiments as ocex
from OCIOexperiments import grading
from OCIOexperiments.gpu.gl import GLImage


logger = logging.getLogger(f"{ocex.c.ABR}.tests_basic")


def setup_logging(level):

    logger = logging.getLogger(ocex.c.ABR)
    logger.setLevel(level)

    if not logger.handlers:
        # create a file handler
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)7s] %(name)30s // %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        # add the file handler to the logger
        logger.addHandler(handler)

    return logger


setup_logging(logging.DEBUG)


def main():

    logger.info("[main] Started.")

    config = ocio.Config().CreateFromFile(
        str(ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio")
    )

    render1 = pxdt.dragonScene.first.path
    render1 = liio.io.read.readToImage(render1)

    opgraph = grading.processes.InToDisplayGradedGraph(
        config=config,
        input_encoding="sRGB",
        target_display="sRGB",
        target_view="Agx Punchy",
        target_looks=None,
    )
    opgraph.grading.exposure = 0.5
    opgraph.grading.saturation = 2.0

    logger.info("[main] GLImage Started.")

    glimage = GLImage(ocio_operation=opgraph)
    glimage.load(image=render1)
    result = glimage.as_array()

    print(result.shape)

    logger.info("[main] Finished.")
    return


if __name__ == "__main__":

    main()
