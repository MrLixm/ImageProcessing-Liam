"""

"""
from __future__ import annotations
import ctypes
import logging
from dataclasses import dataclass
from typing import Union, Optional, ClassVar

import numpy
from OpenGL import GL
import PyOpenColorIO as ocio

from . import c
from . import utils

logger = logging.getLogger(f"{c.ABR}.gl")


def set_texture_filtering(
    texture: Union[GL.GL_TEXTURE_1D, GL.GL_TEXTURE_2D, GL.GL_TEXTURE_3D],
    interpolation: ocio.Interpolation,
):
    """
    Args:
        texture: OpenGL texture type (GL_TEXTURE_1/2/3D)
        interpolation: Interpolation enum value.
    """
    if interpolation == ocio.INTERP_NEAREST:
        GL.glTexParameteri(texture, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(texture, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
    else:
        GL.glTexParameteri(texture, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(texture, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)


def create_texture2d(width: float, height: float) -> str:
    """
    Args:
        width: width of the texture to create
        height: height of the texture to create

    Returns:
        name/identifier of the texture created
    """

    assert (
        width and height
    ), f"[create_texture2d] One of the argument is 0/none: {width} x {height}"

    # generate 1 name of texture for reuse acroos the class
    tex_main = GL.glGenTextures(1)
    GL.glActiveTexture(GL.GL_TEXTURE0)
    # bind this name to a 2D texture
    update_texture_2d(
        texture_id=tex_main,
        array=ctypes.c_void_p(0),
        width=width,
        height=height,
    )

    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
    set_texture_filtering(GL.GL_TEXTURE_2D, ocio.INTERP_LINEAR)

    return tex_main


def update_texture_2d(
    texture_id: str,
    array: Union[numpy.ndarray, ctypes.c_void_p],
    width: float,
    height: float,
):
    """
    Args:
        texture_id: name of the texture to update
        array: image data as pixels representing the texture
        width: width of the texture
        height: height of the texture
    """
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,  # target
        0,  # level
        GL.GL_RGBA32F,  # internal format
        width,  # width
        height,  # height
        0,  # border (always 0)
        GL.GL_RGBA,  # format
        GL.GL_FLOAT,  # type
        array,  # pixels
    )
    return


def compile_shader(glsl_src: str, shader_type: GL.GLenum) -> Optional[GL.GLuint]:
    """

    Args:
        glsl_src:  Shader source code
        shader_type: Type of shader to be created, which is an enum adhering
         to the formatting ``GL_*_SHADER``.

    Returns:
        Shader object ID, or None if shader compilation fails.
    """
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, glsl_src)
    GL.glCompileShader(shader)

    # check if compilation succeed
    if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
        logger.error(
            f"[compile_shader] Shader program compile error: {GL.glGetShaderInfoLog(shader)}"
        )
        return None

    return shader


@dataclass
class Plane:

    vao: str = None
    vbo_position: str = None
    vbo_tex_coord: str = None
    vbo_index: str = None

    _tex_coord: ClassVar[numpy.ndarray] = numpy.array(
        [
            0.0,
            1.0,  # top-left
            1.0,
            1.0,  # top-right
            1.0,
            0.0,  # bottom-right
            0.0,
            0.0,  # bottom-left
        ],
        dtype=numpy.float32,
    )

    _position: ClassVar[numpy.ndarray] = numpy.array(
        [
            -0.5,
            0.5,
            0.0,  # top-left
            0.5,
            0.5,
            0.0,  # top-right
            0.5,
            -0.5,
            0.0,  # bottom-right
            -0.5,
            -0.5,
            0.0,  # bottom-left
        ],
        dtype=numpy.float32,
    )

    _index: ClassVar[numpy.ndarray] = numpy.array(
        [0, 1, 2, 0, 2, 3],  # triangle: top-left  # triangle: bottom-right
        dtype=numpy.uint32,
    )

    @classmethod
    def create(cls) -> Plane:

        plane = Plane()

        plane.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(plane.vao)

        # generate 3 name of buffer objects for re-use
        (
            plane.vbo_position,
            plane.vbo_tex_coord,
            plane.vbo_index,
        ) = GL.glGenBuffers(3)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, plane.vbo_position)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            cls._position.nbytes,
            cls._position,
            GL.GL_STATIC_DRAW,
        )
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, plane.vbo_tex_coord)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            cls._tex_coord.nbytes,
            cls._tex_coord,
            GL.GL_STATIC_DRAW,
        )
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, plane.vbo_index)
        GL.glBufferData(
            GL.GL_ELEMENT_ARRAY_BUFFER,
            cls._index.nbytes,
            cls._index,
            GL.GL_STATIC_DRAW,
        )

        return plane


class GLImage:
    """
    Perform OCIO processing on the GPU for an RGB(A) image.
    Image can be changed at anytime with <load> method.
    """

    def __init__(self):

        self.img_src = utils.V2f(1.0, 1.0)
        """
        texture width*height (x*y) information
        """
        self.tex_main: str = None
        """
        texture name/identifier
        """

        self.plane: Plane = None
        """
        the image plane for viewing the texture
        """

        self.shader_desc: ocio.GpuShaderDesc = None
        self.shader_program = None
        self.shader_vert = None
        self.shader_frag = None

        self.__previous_shader_cache_id = None
        """
        Store the ID of the last OCIO operation to avoid performing 2 times in a row
        the same operation.
        """

        return

    @property
    def _initialized(self):
        """
        Has the instance been initialized a first time.
        """
        # tex_main is no more None once <initialize> is called.
        return True if self.tex_main else False

    def initialize(self):
        """
        Get called once.
        """
        assert not self._initialized, "This instance has already been initalized !"

        self.tex_main = create_texture2d(self.img_src.x, self.img_src.y)
        self.plane = Plane.create()

        logger.debug(f"[{self.__class__.__name__}][initialize] Finished.")
        return

    def build_program(self, force: bool = False):
        """
        Args:
            force: If True, for a rebuild even if the OCIO shader cache ID has not changed.
        """

        assert self._initialized, "Instance has not been initialized yet !"
        assert self.shader_desc, "Instance doesn't have an OCIO Shader desc yet !"

        if (
            not force
            and self.__previous_shader_cache_id == self.shader_desc.getCacheID()
        ):
            logger.debug(
                f"[{self.__class__.__name__}][build_program] Returned early. "
                f"Current cache ID is similar to previous."
            )
            return

        # Init shader program TODO move to initialize ?
        if not self.shader_program:
            self.shader_program = GL.glCreateProgram()

        # Vert shader only needs to be built once TODO move to initialize ?
        if not self.shader_vert:
            self.shader_vert = compile_shader(c.GLSL_VERT_SRC, GL.GL_VERTEX_SHADER)
            if not self.shader_vert:
                logger.debug(
                    f"[{self.__class__.__name__}][build_program] Returned early. "
                    f"No vert shader produced."
                )
                return

            GL.glAttachShader(self.shader_program, self.shader_vert)

        # Frag shader needs recompile each build (for OCIO changes)
        if self.shader_frag:
            GL.glDetachShader(self.shader_program, self.shader_frag)
            GL.glDeleteShader(self.shader_frag)

        # Inject OCIO shader block
        frag_src = c.GLSL_FRAG_OCIO_SRC_FMT.format(
            ocio_src=self.shader_desc.getShaderText()
        )
        self.shader_frag = compile_shader(frag_src, GL.GL_FRAGMENT_SHADER)
        if not self.shader_frag:
            logger.debug(
                f"[{self.__class__.__name__}][build_program] Returned early. "
                f"No frag shader produced."
            )
            return
        GL.glAttachShader(self.shader_program, self.shader_frag)

        # Link program
        GL.glBindAttribLocation(self.shader_program, 0, "in_position")
        GL.glBindAttribLocation(self.shader_program, 1, "in_texCoord")

        GL.glLinkProgram(self.shader_program)
        link_status = GL.glGetProgramiv(self.shader_program, GL.GL_LINK_STATUS)
        assert link_status, (
            f"Shader program link error: "
            f"{GL.glGetProgramInfoLog(self.shader_program)}"
        )

        # Store cache ID to detect reuse
        self.__previous_shader_cache_id = self.shader_desc.getCacheID()

        logger.debug(f"[{self.__class__.__name__}][build_program] Finished.")
        return

    def load(self, array: numpy.ndarray):
        """

        Args:
            array: expecting a 32bit float image encoded as R-G-B(-A)

        Returns:

        """

        logger.debug(f"[{self.__class__.__name__}][load] Finished.")
        return
