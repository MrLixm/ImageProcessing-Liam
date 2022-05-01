"""

"""
import logging
import sys
from typing import List

import WebcamLiveProcessing as wlp
import OCIOexperiments as ocex


logger = logging.getLogger(f"{wlp.c.ABR}.tests_main")


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
    # wlp.main.run3(camera=cam_c922)
    wlp.main.run4live(camera=cam_c922, method="ocio", debug=True)

    logger.info("//// Finished.")
    return


if __name__ == "__main__":

    run()
