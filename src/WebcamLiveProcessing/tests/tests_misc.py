"""
"""
import logging
import sys
import time
from pathlib import Path
from typing import Literal, List, Union

import cv2
import numpy
import pyvirtualcam
from pyvirtualcam import PixelFormat

import WebcamLiveProcessing as wlp
import OCIOexperiments as ocex

logger = logging.getLogger(f"{wlp.c.ABR}.tests_misc")


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


def live_exposure(
    camera: wlp.Webcam,
    exposure: float = 1,
    exposure_mode: Literal["scene", "display"] = "scene",
    debug: bool = False,
):
    """
    Basic example from
    https://github.com/letmaik/pyvirtualcam/blob/main/examples/webcam_filter.py

    Args:
        exposure_mode: apply exposure on scene or display referred data.
            display referred is much faster.
        debug:
        exposure:
        camera:

    """

    with pyvirtualcam.Camera(
        width=camera.width,
        height=camera.height,
        fps=camera.fps,
        fmt=PixelFormat.RGB,
        print_fps=debug,
    ) as vcam:

        logger.info(
            f"[live_exposure] pyvirtualcam started: {vcam.device} "
            f"({vcam.width}x{vcam.height})@{vcam.fps}fps)"
        )

        while True:
            ret, frame = camera.read()
            frame: numpy.ndarray
            if not ret:
                raise RuntimeError("Error fetching frame")

            new_image: numpy.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # convert to float
            new_image = new_image.astype(numpy.float32)
            new_image /= 255
            # linearize
            if exposure_mode == "scene":
                new_image = new_image**2.2
            # apply gain
            new_image = new_image * exposure
            new_image = new_image.clip(0, 1)
            # apply back EOTF
            if exposure_mode == "scene":
                new_image = new_image ** (1 / 2.2)
            # convert back to 8bit
            new_image *= 255
            new_image = new_image.astype(numpy.uint8)

            vcam.send(new_image)

            # Wait until it's time for the next frame.
            vcam.sleep_until_next_frame()

    logger.info("[live_exposure] Finished.")
    return


def sream2image1(camera: wlp.Webcam):

    export_path = wlp.c.OUTPUT_DIR / "0002" / "webcam.$FRAME.tif"

    t_end = time.time() + 3  # in seconds
    timeframe = 1

    logger.info("[run2] Started.")

    while time.time() < t_end:

        ret, current_image = camera.read()
        current_image: numpy.ndarray
        assert ret, "Error fetching current frame from videocapture."

        # current_image = current_image[:, :, ::-1]  # BGR to RGB
        # reinterpret data as 16-bit pixels
        # current_image: numpy.ndarray = current_image.view(dtype=numpy.int16)
        # # # Shift away the bottom 2 bits
        # current_image: numpy.ndarray = numpy.right_shift(current_image, 2)
        # current_image: numpy.ndarray = (
        #     current_image[0].reshape(3, 720, 1280).transpose(1, 2, 0)
        # )

        # current_image = cv2.imdecode(current_image, cv2.IMREAD_COLOR)

        export_path = str(export_path).replace("$FRAME", str(timeframe))
        cv2.imwrite(export_path, current_image)
        logger.info(f"[run2] File exported to {export_path}")

        timeframe += 1

    camera.release()
    cv2.destroyAllWindows()

    logger.info("[run2] Finished.")
    return


def sream2image2(camera: wlp.Webcam, duration: int = 3):
    """
    Run the webcam during the given time and apply an OCIO processingon each frame that
    are then written to disk.

    Args:
        camera:
        duration: time the webcam is activated in second
    """

    export_path = wlp.c.OUTPUT_DIR / "run3" / "webcam.$FRAME.tif"
    if not export_path.parent.exists():
        export_path.parent.mkdir()

    t_end = time.time() + duration  # in seconds
    timeframe = 0

    logger.info("[run3] Started.")

    while time.time() < t_end:

        ret, current_image = camera.read()
        current_image: numpy.ndarray
        assert ret, "Error fetching current frame from videocapture."

        new_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        new_image = new_image.astype(numpy.float32)
        new_image /= 255
        new_image = ocex.agxc.transforms.transform_inout_look_1(new_image)

        _export_path = Path(str(export_path).replace("$FRAME", str(timeframe)))
        ocex.io.array_write(new_image, _export_path, numpy.uint8, method="pillow")

        timeframe += 1

    camera.release()
    cv2.destroyAllWindows()

    logger.info("[run3] Finished.")
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
    live_exposure(camera=cam_c922, exposure=2, debug=True)

    logger.info("//// Finished.")
    return


if __name__ == "__main__":

    run()
