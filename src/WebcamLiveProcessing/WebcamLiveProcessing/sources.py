"""

"""
import argparse
import logging
import time
from dataclasses import dataclass
from functools import cached_property
from typing import Union

import cv2

from . import c

__all__ = [
    "WebcamConfiguration",
    "Webcam",
]

logger = logging.getLogger(f"{c.ABR}.sources")


@dataclass
class WebcamConfiguration:
    name: str
    """
    name of the stream. Usually the name of the video recording camera.
    """

    camera: int
    """
    Identifier for the camera source to pick. Try with 0 first if you don't know.
    """

    target_width: int = None
    target_height: int = None
    target_fps: Union[int, float] = None

    convert_rgb: Union[bool, int] = None
    """
    Boolean flags indicating whether images should be converted to RGB.
    """

    fourcc: str = None
    """
    4-character code of codec
    """

    mode: str = None
    """
    Backend-specific value indicating the current capture mode.
    """

    format: int = None
    """
    Set value -1 to fetch undecoded RAW video streams.
    """

    def __post_init__(self):
        # bug in OpenCV 4 where it needs an int
        if self.convert_rgb is not None:
            self.convert_rgb: int = int(self.convert_rgb)
        return

    @cached_property
    def properties(self) -> dict:

        out = {
            cv2.CAP_PROP_FRAME_WIDTH: self.target_width,
            cv2.CAP_PROP_FRAME_HEIGHT: self.target_height,
            cv2.CAP_PROP_FPS: self.target_fps,
            cv2.CAP_PROP_CONVERT_RGB: self.convert_rgb,
            cv2.CAP_PROP_FOURCC: self.fourcc,
            cv2.CAP_PROP_MODE: self.mode,
            cv2.CAP_PROP_FORMAT: self.format,
        }
        out = {k: v for k, v in out.items() if v is not None}
        return out


class Webcam(cv2.VideoCapture):
    def __init__(self, configuration: WebcamConfiguration):

        _stime = time.time()

        self.config = configuration

        logger.info(
            f"[{self.__class__.__name__}][__init__] Started, "
            f"this can take a few seconds ..."
        )

        super().__init__(configuration.camera)
        assert self.isOpened(), f"Could not open video source <{configuration.name}>"

        self.build()

        logger.debug(
            f"[{self.__class__.__name__}][__init__] VideoCapture instance created in "
            f"{time.time() - _stime}s."
        )
        return

    def __repr__(self) -> str:
        return (
            f"[{super().__repr__()}]({self.width}x{self.height})@{self.fps}fps. "
            f"[config]({self.config.target_width}x{self.config.target_height})"
            f"@{self.config.target_fps}fps."
        )

    def build(self):

        for k, v in self.config.properties.items():
            self.set(k, v)

        return

    @property
    def width(self) -> int:
        return int(self.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self) -> int:
        return int(self.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def fps(self) -> float:
        return float(self.get(cv2.CAP_PROP_FPS))


def get_configuration_cli() -> argparse.Namespace:
    """
    TODO refactor this.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--camera", type=int, default=0, help="ID of webcam device (default: 0)"
    )
    parser.add_argument(
        "--display_fps", action="store_true", help="output fps every second"
    )
    parser.add_argument("--filter", choices=["shake", "none"], default="shake")
    return parser.parse_args()
