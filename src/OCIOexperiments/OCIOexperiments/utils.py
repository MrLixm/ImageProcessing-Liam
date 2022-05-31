"""

"""
import logging
from typing import (
    Optional,
)

import PyOpenColorIO as ocio

from . import c

__all__ = ("update_shader_dyn_prop",)


logger = logging.getLogger(f"{c.ABR}.utils")


def update_shader_dyn_prop(
    shader: ocio.GpuShaderDesc,
    prop_type: ocio.DynamicPropertyType,
    value,
) -> Optional[ocio.DynamicProperty]:
    """
    Used for GPU.
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

    if shader.hasDynamicProperty(prop_type):
        dyn_prop: ocio.DynamicProperty = shader.getDynamicProperty(prop_type)
        if prop_type is ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY:
            dyn_prop.setGradingPrimary(value)
        elif prop_type is ocio.DYNAMIC_PROPERTY_GRADING_RGBCURVE:
            dyn_prop.setGradingRGBCurve(value)
        elif prop_type is ocio.DYNAMIC_PROPERTY_GRADING_TONE:
            dyn_prop.setGradingTone(value)
        else:
            dyn_prop.setDouble(value)
        return dyn_prop
