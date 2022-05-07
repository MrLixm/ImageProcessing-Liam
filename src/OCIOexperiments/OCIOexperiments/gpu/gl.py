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
from . import main
from . import glUtils
from . import ocioUtils

logger = logging.getLogger(f"{c.ABR}.gl")


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
    Image apperance can also be modified interactively using <transform_interactive>.
    """

    def __init__(self):

        self.ocioops: ocioUtils.OcioOperationGraph = None

        self.img_src: main.ImageContainer = None
        """
        Whole 32bit float Image.
        """
        self.__tex_main: str = None
        """
        texture name/identifier
        """

        self.__plane: Plane = None
        """
        the image plane for viewing the texture
        """

        self.transform_interactive: main.InteractiveLook = main.InteractiveLook()
        """
        Common color transformations values that can be modified interactively
        by the user. 
        """

        # OpenGL shaders
        self.shader_desc: ocio.GpuShaderDesc = None
        self.shader_program = None
        self.shader_vert = None
        self.shader_frag = None

        self.__previous_shader_cache_id = None
        """
        Stores the ID of the last OCIO operation to avoid performing 2 times in a row
        the same operation.
        """

        return

    @property
    def _initialized(self):
        """
        Has the instance been initialized a first time.
        """
        # tex_main is no more None once <initialize> is called.
        return True if self.__tex_main else False

    def initialize(self):
        """
        Get called once.
        """
        assert not self._initialized, "This instance has already been initalized !"

        self.__tex_main = glUtils.create_texture2d(
            self.img_src.width, self.img_src.height
        )
        self.__plane = Plane.create()

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
            self.shader_vert = glUtils.compile_shader(
                c.GLSL_VERT_SRC, GL.GL_VERTEX_SHADER
            )
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
        self.shader_frag = glUtils.compile_shader(frag_src, GL.GL_FRAGMENT_SHADER)
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

    def load(self, image: main.ImageContainer):
        """

        Args:
            image: expecting a 32bit float image encoded as R-G-B(-A)

        Returns:

        """
        self.img_src = image

        if not self._initialized:
            self.initialize()

        glUtils.update_texture_2d(
            texture_id=self.__tex_main,
            array=image.array.ravel(),
            width=image.width,
            height=image.height,
        )

        self._update_model_view_mat()
        self._update_ocio_proc()

        logger.debug(f"[{self.__class__.__name__}][load] Finished for {image} .")
        return

    def _update_model_view_mat(self):
        """
        Re-calculate the model view matrix, which needs to be updated
        prior to rendering if the image or window size have changed.
        """
        pass

    def _update_ocio_proc(self):
        """
        Update one or more aspects of the OCIO GPU renderer. Parameters
        are cached so not providing a parameter maintains the existing
        state. This will trigger a GL update IF the underlying OCIO ops
        in the processor have changed.
        """
        assert self.ocioops, "[load] No OcioOperationGraph has been supplied yet !"

        return
