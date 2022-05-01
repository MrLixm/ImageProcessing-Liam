"""
This scripts uses OpenCV to capture webcam output, applies a filter,
and sends it to the virtual camera.
It also shows how to use BGR as pixel format.
"""
import logging
import time
from pathlib import Path
from typing import Literal, List, Union

import cv2
import numpy
import pyvirtualcam
from pyvirtualcam import PixelFormat
import OCIOexperiments as ocex

from . import c
from . import sources

logger = logging.getLogger(f"{c.ABR}.main")


def run1live(camera: sources.Webcam):
    """
    Basic example from
    https://github.com/letmaik/pyvirtualcam/blob/main/examples/webcam_filter.py

    Args:
        camera:

    """

    with pyvirtualcam.Camera(
        width=camera.width,
        height=camera.height,
        fps=camera.fps,
        fmt=PixelFormat.RGB,
        print_fps=False,
    ) as vcam:

        logger.info(
            f"[run1] pyvirtualcam started: {vcam.device} ({vcam.width}x{vcam.height})"
            f"@{vcam.fps}fps)"
        )

        while True:
            ret, frame = camera.read()
            frame: numpy.ndarray
            if not ret:
                raise RuntimeError("Error fetching frame")

            vcam.send(frame)

            # Wait until it's time for the next frame.
            vcam.sleep_until_next_frame()

    logger.info("[run1] Finished.")
    return


def run2(camera: sources.Webcam):

    export_path = c.OUTPUT_DIR / "0002" / "webcam.$FRAME.tif"

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


def run3(camera: sources.Webcam, duration: int = 3):
    """
    Run the webcam during the given time and apply an OCIO processingon each frame that
    are then written to disk.

    Args:
        camera:
        duration: time the webcam is activated in second
    """

    export_path = c.OUTPUT_DIR / "run3" / "webcam.$FRAME.tif"
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
        new_image = ocex.basic.transform_array_1(new_image)

        _export_path = Path(str(export_path).replace("$FRAME", str(timeframe)))
        ocex.io.array_write(new_image, _export_path, numpy.uint8, method="pillow")

        timeframe += 1

    camera.release()
    cv2.destroyAllWindows()

    logger.info("[run3] Finished.")
    return


def run4live(camera: sources.Webcam, method: Literal["ocio", "native"], debug=False):
    """
    VirtualCamera stream with AgX

    Args:
        method:
        camera:
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
            f"[run1] pyvirtualcam started: {vcam.device} ({vcam.width}x{vcam.height})"
            f"@{vcam.fps}fps)"
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

    logger.info("[run4live] Finished.")
    return
