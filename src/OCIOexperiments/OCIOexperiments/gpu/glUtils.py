"""

"""
from __future__ import annotations
import ctypes
import logging
from typing import Union, Optional

import numpy
from OpenGL import GL
import PyOpenColorIO as ocio

from . import c


logger = logging.getLogger(f"{c.ABR}.glUtils")


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
    Create a 32bit float RGBA texture.

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
        array:
            image data as pixels representing the texture.
            think to flaten the array beofre.
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


def create_texture(
    texture_type: Union[GL.GL_TEXTURE_1D, GL.GL_TEXTURE_2D, GL.GL_TEXTURE_3D],
    texture_info: ocio.GpuShaderDesc.Texture,
    texture_id: str,
    texture_active_id: int,
    format_texture=GL.GL_RGB32F,
    format_pixels=GL.GL_RGB,
):
    """
    Args:
        texture_type: 1D, 2D or 3D
        texture_info: GPU texture queried from the GpuShaderDesc
        texture_id: name of the current texture
        texture_active_id: identifier for the currently active texture
        format_texture: (internalFormat) Number of color components in the texture
        format_pixels:  format of the pixel data
    """

    # 3D
    GL.glActiveTexture(texture_active_id)
    GL.glBindTexture(texture_type, texture_id)
    set_texture_filtering(texture_type, texture_info.interpolation)

    if texture_type == GL.GL_TEXTURE_3D:
        GL.glTexImage3D(
            texture_type,
            0,
            format_texture,
            texture_info.edgeLen,
            texture_info.edgeLen,
            texture_info.edgeLen,
            0,
            format_pixels,
            GL.GL_FLOAT,
            texture_info.getValues(),
        )

    elif texture_type == GL.GL_TEXTURE_2D:
        GL.glTexImage2D(
            texture_type,
            0,
            format_texture,
            texture_info.width,
            texture_info.height,
            0,
            format_pixels,
            GL.GL_FLOAT,
            texture_info.getValues(),
        )
    elif texture_type == GL.GL_TEXTURE_1D:
        GL.glTexImage1D(
            texture_type,
            0,
            format_texture,
            texture_info.width,
            0,
            format_pixels,
            GL.GL_FLOAT,
            texture_info.getValues(),
        )

    else:
        raise ValueError(f"Unsupported texture_type <{texture_type}>")
