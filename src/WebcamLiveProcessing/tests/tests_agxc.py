"""

"""
import logging
import sys
from typing import List, Literal

import cv2
import numpy
import pyvirtualcam
from pyvirtualcam import PixelFormat

import WebcamLiveProcessing as wlp
import OCIOexperiments as ocex


logger = logging.getLogger(f"{wlp.c.ABR}.tests_agxc")


def setup_logging(level, loggers: List[str]):

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    # create a logging format
    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)7s] %(name)30s // %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    for logger_name in loggers:

        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        # add the file handler to the logger
        if not logger.handlers:
            logger.addHandler(handler)

    return


setup_logging(logging.DEBUG, loggers=[wlp.c.ABR, ocex.c.ABR])

"""
---------------------------------------------------------------------------------------
"""


def livefeed_agxc(camera: wlp.Webcam, method: Literal["ocio", "native"], debug=False):
    """
    VirtualCamera stream with AgX

    Args:
        camera:
        method: ocio is faster than native
        debug: if true display per-frame info like fps
    """

    if method == "ocio":
        colortransform = ocex.agxc.transforms.transform_inout_look_1
    elif method == "native":
        colortransform = ocex.agxc.transforms.transform_native_inout_look_1

    with pyvirtualcam.Camera(
        width=camera.width,
        height=camera.height,
        fps=camera.fps,
        fmt=PixelFormat.RGB,
        print_fps=debug,
    ) as vcam:

        logger.info(
            f"[livefeed_agxc] pyvirtualcam started: {vcam.device} "
            f"({vcam.width}x{vcam.height})@{vcam.fps}fps)"
        )

        while True:
            ret, current_image = camera.read()
            current_image: numpy.ndarray
            assert ret, "Error fetching current frame from videocapture."

            new_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
            new_image = new_image.astype(numpy.float32)
            new_image /= 255
            new_image = colortransform(new_image)
            new_image *= 255
            new_image = new_image.astype(numpy.uint8)

            vcam.send(new_image)

            # Wait until it's time for the next frame.
            vcam.sleep_until_next_frame()

    logger.info("[livefeed_agxc] Finished.")
    return


def run():

    logger.info("//// Started.")

    config = wlp.sources.WebcamConfiguration(
        camera=0,
        name="c922pro",
        target_width=1280,
        target_height=720,
        target_fps=30,
    )
    cam_c922 = wlp.sources.Webcam(configuration=config)

    # start process
    livefeed_agxc(camera=cam_c922, method="ocio", debug=True)

    logger.info("//// Finished.")
    return


if __name__ == "__main__":

    run()
