"""

"""
from __future__ import annotations
import ctypes
import logging
from dataclasses import dataclass
from typing import Union, ClassVar

import numpy
from OpenGL import GL
import PyOpenColorIO as ocio
import lxmImageIO as liio

from . import c
from . import main
from . import glUtils
from .. import grading

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


# noinspection PyPep8Naming
class GLImage:
    """
    Perform OCIO processing on the GPU for an RGB(A) image.
    Image can be changed at anytime with <load> method.
    Image apperance can also be modified interactively using <transform_interactive>.

    Args:
        ocio_operation:
            OCIO operations to apply on the image. Modified in live by the user.
    """

    # noinspection PyTypeChecker
    def __init__(self, ocio_operation: grading.processes.BaseOpGraph):

        self.ocioops: grading.processes.BaseOpGraph = ocio_operation
        """
        OCIO operations to apply on the image. Can be modified live by the user.
        """

        self.image: liio.containers.ImageContainer = None
        """
        Whole 32bit float Image.
        """
        self._tex_main: str = None
        """
        texture name/identifier
        """

        self._textures_ids = list()
        self._uniforms_ids = dict()
        self._texture_index_buf = 1
        """
        Buffer for number of texture created in a run.
        """

        self._plane: Plane = None
        """
        the image plane for viewing the texture
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

        logger.debug(f"[{self.__class__.__name__}][__init__] Finished.")
        return

    @property
    def _initialized(self):
        """
        Has the instance been initialized a first time.
        """
        # tex_main is no more None once <initialize> is called.
        return True if self._tex_main else False

    def initializeGL(self):
        """
        Get called once.
        Requires shader_desc to be intialized.
        """
        assert not self._initialized, "This instance has already been initalized !"

        self._tex_main = glUtils.create_texture2d(self.image.width, self.image.height)
        self._plane = Plane.create()

        self.build_program()

        logger.debug(f"[{self.__class__.__name__}][initializeGL] Finished.")
        return

    def paintGL(self):
        """
        Called whenever a repaint is needed. Calling ``update()`` will
        schedule a repaint.
        """
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if self.shader_program is None:
            logger.debug(
                f"[{self.__class__.__name__}][paintGL] Returned early. "
                f"No shader program yet."
            )
            return

        GL.glUseProgram(self.shader_program)

        self._use_textures_ocio()
        self._use_uniforms_ocio()

        # Set uniforms TODO check what to do
        # mvp_mat = self._proj_mat * self._model_view_mat
        # mvp_mat_loc = GL.glGetUniformLocation(self.shader_program, "mvpMat")
        # GL.glUniformMatrix4fv(
        #     mvp_mat_loc, 1, GL.GL_FALSE, self._m44f_to_ndarray(mvp_mat)
        # )

        image_tex_loc = GL.glGetUniformLocation(self.shader_program, "imageTex")
        GL.glUniform1i(image_tex_loc, 0)

        # Bind texture, VAO, and draw
        GL.glActiveTexture(GL.GL_TEXTURE0 + 0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_main)

        GL.glBindVertexArray(self._plane.vao)

        GL.glDrawElements(
            GL.GL_TRIANGLES,
            6,
            GL.GL_UNSIGNED_INT,
            ctypes.c_void_p(0),
        )

        GL.glBindVertexArray(0)

        logger.debug(f"[{self.__class__.__name__}][paintGL] Finished.")
        return

    def as_array(self) -> numpy.ndarray:
        return GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, GL.GL_FLOAT)

    def build_program(self, force: bool = False):
        """
        Args:
            force: If True, for a rebuild even if the OCIO shader cache ID has not changed.
        """

        assert self._initialized, "Instance has not been initialized yet !"
        # assert self.shader_desc, "Instance doesn't have an OCIO Shader desc yet !"

        if (
            self.shader_desc
            and not force
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

        # Use default or Inject OCIO shader block
        frag_src = c.GLSL_FRAG_SRC
        if self.shader_desc:
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
        if self.shader_desc:
            self.__previous_shader_cache_id = self.shader_desc.getCacheID()

        logger.debug(f"[{self.__class__.__name__}][build_program] Finished.")
        return

    def load(self, image: liio.containers.ImageContainer):
        """
        Args:
            image: expecting a 32bit float image encoded as R-G-B(-A)
        """
        logger.debug(f"[{self.__class__.__name__}][load] Started for image {image} .")

        self.image = image

        if not self._initialized:
            self.initializeGL()

        glUtils.update_texture_2d(
            texture_id=self._tex_main,
            array=image.array.ravel(),
            width=image.width,
            height=image.height,
            alpha=image.channels == 4,
        )

        logger.debug(f"[{self.__class__.__name__}][load] Updated_texture_2d .")

        self._update_model_view_mat()
        self._update_ocio_proc()

        logger.debug(f"[{self.__class__.__name__}][load] Finished for {image} .")
        return

    def update(self):
        # this was originaly a QWidget method to redraw the widget
        self.paintGL()

    # TODO _update_model_view_mat
    def _update_model_view_mat(self, update_widget=True):
        """
        Re-calculate the model view matrix, which needs to be updated
        prior to rendering if the image or window size have changed.

        Args:
            update_widget: redraw the window if true
        """
        if update_widget:
            self.update()
        return

    def _update_ocio_proc(
        self,
        force=False,
    ):
        """
        Update one or more aspects of the OCIO GPU renderer. Parameters
        are cached so not providing a parameter maintains the existing
        state. This will trigger a GL update IF the underlying OCIO ops
        in the processor have changed.

        Args:
            force: if True force re-processing even if the proc cacheID is similar
                to the previously runned one.
        """
        assert self.ocioops, "[load] No InToDisplayGradedGraph has been supplied yet !"

        proc = self.ocioops.get_proc()
        if proc.getCacheID() == self.__previous_shader_cache_id and not force:
            logger.debug(
                f"[{self.__class__.__name__}][_update_ocio_proc] Returned early. "
                f"Current cache ID is similar to previous."
            )
            return

        self.__previous_shader_cache_id = proc.getCacheID()

        # noinspection PyArgumentList
        self.shader_desc = ocio.GpuShaderDesc.CreateShaderDesc(
            language=ocio.GPU_LANGUAGE_GLSL_4_0
        )
        ocio_gpu_proc = proc.getDefaultGPUProcessor()
        ocio_gpu_proc.extractGpuShaderInfo(self.shader_desc)

        self._allocate_textures()
        self.build_program()

        # Set initial dynamic property state
        self.ocioops.grading.update_all_shader_dyn_prop(shader=self.shader_desc)
        self.update()

        logger.debug(f"[{self.__class__.__name__}][_update_ocio_proc] Finished.")
        return

    def _add_texture(
        self,
        texture_type: Union[GL.GL_TEXTURE_1D, GL.GL_TEXTURE_2D, GL.GL_TEXTURE_3D],
        texture_info: ocio.GpuShaderDesc.Texture,
        red_only: bool = False,
    ) -> str:
        """

        Args:
            texture_type: 1D, 2D or 3D
            texture_info: GPU texture queried from the GpuShaderDesc
            red_only: True if the passed texture is single channel (RED only)

        Returns:
            identifier of the texture generated
        """

        tex_id = GL.glGenTextures(1)

        GL.glActiveTexture(GL.GL_TEXTURE0 + self._texture_index_buf)
        GL.glBindTexture(texture_type, tex_id)
        glUtils.set_texture_filtering(texture_type, texture_info.interpolation)

        fmt_tx = GL.GL_R32F if red_only else GL.GL_RGB32F
        fmt_px = GL.GL_RED if red_only else GL.GL_RGB

        glUtils.create_texture(
            texture_type=texture_type,
            texture_info=texture_info,
            texture_id=tex_id,
            texture_active_id=self._texture_index_buf,
            format_texture=fmt_tx,
            format_pixels=fmt_px,
        )

        self._textures_ids.append(
            (
                tex_id,
                texture_info.textureName,
                texture_info.samplerName,
                texture_type,
                self._texture_index_buf,
            )
        )
        self._texture_index_buf += 1

        return tex_id

    def _allocate_textures(self):
        """
        Iterate and allocate 1/2/3D textures needed by the current
        OCIO GPU processor. 3D LUTs become 3D textures and 1D LUTs
        become 1D or 2D textures depending on their size. Since
        textures have a hardware enforced width limitation, large LUTs
        are wrapped onto multiple rows.

        Notes:
            Each time this runs, the previous set of textures are
            deleted from GPU memory first.
        """
        assert self.shader_desc, "Instance doesn't have an OCIO Shader desc yet !"

        # Delete previous textures
        self._del_textures_ocio()
        self._use_uniforms_ocio()

        # reset index buffer
        self._texture_index_buf = 1

        # Process 3D textures
        tex_info: ocio.GpuShaderDesc.Texture
        for tex_info in self.shader_desc.get3DTextures():

            self._add_texture(
                texture_type=GL.GL_TEXTURE_3D,
                texture_info=tex_info,
            )

        # Process 2D textures
        for tex_info in self.shader_desc.getTextures():

            # is single channel (RED)
            redonly = tex_info.channel == self.shader_desc.TEXTURE_RED_CHANNEL
            textype = GL.GL_TEXTURE_2D if tex_info.height > 1 else GL.GL_TEXTURE_1D

            self._add_texture(
                texture_type=textype,
                texture_info=tex_info,
                red_only=redonly,
            )

        return

    def _use_textures_ocio(self):
        """
        Bind all OCIO textures to the shader program.
        """
        for tex, tex_name, sampler_name, tex_type, tex_index in self._textures_ids:
            GL.glActiveTexture(GL.GL_TEXTURE0 + tex_index)
            GL.glBindTexture(tex_type, tex)
            GL.glUniform1i(
                GL.glGetUniformLocation(self.shader_program, sampler_name),
                tex_index,
            )

        return

    def _del_textures_ocio(self):
        """
        Delete all OCIO textures from the GPU.
        """
        for tex, tex_name, sampler_name, tex_type, tex_index in self._textures_ids:
            GL.glDeleteTextures([tex])

        del self._textures_ids[:]
        return

    def _use_uniforms_ocio(self):
        """
        Bind and/or update dynamic property uniforms needed for the
        current OCIO shader build.
        """
        if not self.shader_desc or not self.shader_program:
            return

        for name, uniform_data in self.shader_desc.getUniforms():

            if name not in self._uniforms_ids:
                uid = GL.glGetUniformLocation(self.shader_program, name)
                self._uniforms_ids[name] = uid
            else:
                uid = self._uniforms_ids[name]

            if uniform_data.type == ocio.UNIFORM_DOUBLE:
                GL.glUniform1f(uid, uniform_data.getDouble())

        return

    def _del_uniforms_ocio(self):
        """
        Forget about the dynamic property uniforms needed for the
        previous OCIO shader build.
        """
        self._uniforms_ids.clear()
