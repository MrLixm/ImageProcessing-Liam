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


@contextmanager
def create_window(dimensions: Tuple[int, int] = (1280, 720), hidden: bool = True):
    """
    to use as context (``with display_window(...)``)

    SRC: https://www.pygame.org/wiki/SimpleOpenGL2dClasses

    Args:
        hidden:
        dimensions: width x height

    Returns:

    """
    screen = None
    hidden = pygame.HIDDEN if hidden else pygame.SHOWN

    try:
        pygame.init()
        screen = pygame.display.set_mode(
            dimensions, pygame.OPENGL | pygame.DOUBLEBUF  # & hidden
        )

        # GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        # GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        #
        # GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glLoadIdentity()
        # # this puts us in quadrant 1, rather than quadrant 4
        # GLU.gluOrtho2D(0, dimensions[0], dimensions[1], 0)
        # GL.glMatrixMode(GL.GL_MODELVIEW)

        # set up texturing
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # GLU.gluPerspective(90, (dimensions[0] / dimensions[1]), 0.01, 12)

        logger.info(f"[window] pygame window {screen} of size {dimensions} created.")
        yield screen

    finally:
        pygame.quit()
        logger.info(f"[window] Closed pygame window {screen}")
