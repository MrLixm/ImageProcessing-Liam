"""

"""
import logging
import sys

import OCIOexperiments as ocex

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


ocex.basic.run1()

logger.info("Finished.")
