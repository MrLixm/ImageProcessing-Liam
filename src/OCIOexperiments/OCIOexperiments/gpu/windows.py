"""

"""
import logging
from typing import Tuple

import pygame
from OpenGL import GL
from OpenGL import GLU
from contextlib import contextmanager

from . import c

logger = logging.getLogger(f"{c.ABR}.windowCreate")


def window_init(dimensions: Tuple[int, int] = (1280, 720), hidden: bool = True):
    """
    Args:
        hidden:
        dimensions: width x height

    Returns:

    """

    screen = None
    hidden = pygame.HIDDEN if hidden else pygame.SHOWN
    pygame.init()
    screen = pygame.display.set_mode(
        dimensions, pygame.OPENGL | pygame.DOUBLEBUF | hidden
    )
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    logger.info(f"[window] pygame window {screen} of size {dimensions} created.")

    return screen


@contextmanager
def window_instance(dimensions: Tuple[int, int] = (1280, 720), hidden: bool = True):
    """
    to use as context (``with display_window(...)``)

    SRC: https://www.pygame.org/wiki/SimpleOpenGL2dClasses

    Args:
        hidden:
        dimensions: width x height

    Returns:

    """
    screen = None
    try:
        screen = window_init(dimensions=dimensions, hidden=hidden)
        yield screen

    finally:
        pygame.quit()
        logger.info(f"[window] Closed pygame window {screen}")
