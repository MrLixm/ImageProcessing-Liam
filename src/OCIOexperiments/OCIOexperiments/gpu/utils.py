"""

"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

import PyOpenColorIO as ocio

__all__ = [
    "V2f",
    "update_shader_dyn_prop",
]

import numpy


@dataclass
class V2f:
    x: float
    y: float


@dataclass
class ImageSimple:

    path: str
    width: float
    height: float
    array: numpy.ndarray


def update_shader_dyn_prop(
    shader: Optional[ocio.GpuShaderDesc],
    prop_type: ocio.DynamicPropertyType,
    value,
) -> Optional[ocio.DynamicProperty]:
    """
    Update a specific OCIO dynamic property, which will be passed
    to the shader program as a uniform.

    Args:
        shader:
        prop_type:
            Property type to update. Only one dynamic property per type is supported
            per processor, so only the first will be updated if there are multiple.
        value:
            An appropriate value for the specific property type.

    Returns:
        the DynamicProperty from the shader that has been edited for potential further
        modification.
    """
    if not shader:
        return  # TODO see if just return or remove this

    if shader.hasDynamicProperty(prop_type):
        dyn_prop: ocio.DynamicProperty = shader.getDynamicProperty(prop_type)
        dyn_prop.setDouble(value)
        return dyn_prop
