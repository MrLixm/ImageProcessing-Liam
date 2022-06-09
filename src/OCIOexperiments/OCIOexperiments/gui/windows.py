"""

"""
import logging
from typing import Tuple

import pygame
from OpenGL import GL
from contextlib import contextmanager

from . import c

logger = logging.getLogger(f"{c.ABR}.windowCreate")


def window_init(dimensions: Tuple[int, int] = (1280, 720), hidden: bool = False):
    """
    Create and initialize a pygame window.

    SRC: https://www.pygame.org/wiki/SimpleOpenGL2dClasses

    Args:
        hidden:
        dimensions: width x height

    Returns:

    """

    hidden = pygame.HIDDEN if hidden else pygame.SHOWN
    pygame.init()
    wind = pygame.display.set_mode(
        dimensions, pygame.OPENGL | pygame.DOUBLEBUF | hidden
    )
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    logger.info(f"[window_init] pygame window {wind} of size {dimensions} created.")
    return wind


@contextmanager
def window_instance(dimensions: Tuple[int, int] = (1280, 720), hidden: bool = True):
    """
    Open and close a window in context.

    Args:
        hidden:
        dimensions: width x height

    Returns:

    """
    wind = None
    try:
        wind = window_init(dimensions=dimensions, hidden=hidden)
        yield wind

    finally:
        pygame.quit()
        logger.info(f"[window_instance] Closed pygame window {wind}")
