"""

"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Union, Dict

import PyOpenColorIO as ocio

from . import c

__all__ = ("update_shader_dyn_prop", "OcioOperationGraph")


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


@dataclass
class InteractiveLook:

    exposure: float = 1.0
    gamma: float = 1.0

    # GradingPrimary
    contrast: float = 0.0
    pivot: float = 0.18
    saturation: float = 1.0

    grading_space = ocio.GRADING_LIN
    """
    Choose in which space must some of the interactive color grading operations are 
    performed. This will not affect *exposure* and *gamma* adjustements.

    For now the input image has to be encoded in the same format (so log transfer-function
     if GRADING_LOG).

    Can be one of :

    - ocio.GRADING_LIN
    - ocio.GRADING_LOG
    - ocio.GRADING_VIDEO
    """

    @property
    def grading_primary(self) -> ocio.GradingPrimary:
        gp = ocio.GradingPrimary(self.grading_space)
        gp.saturation = self.saturation
        gp.contrast = self.contrast
        gp.pivot = self.pivot
        return gp

    @property
    def dynamic_props(
        self,
    ) -> Dict[ocio.DynamicPropertyType, Union[float, ocio.GradingPrimary]]:
        return {
            ocio.DYNAMIC_PROPERTY_EXPOSURE: self.exposure,
            ocio.DYNAMIC_PROPERTY_GAMMA: self.gamma,
            ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY: self.grading_primary,
        }

    def __repr__(self) -> dict:
        return {
            "exposure": self.exposure,
            "gamma": self.gamma,
            "grading_space": str(self.grading_space),
            "contrast": self.contrast,
            "pivot": self.pivot,
            "saturation": self.saturation,
        }


class OcioOperationGraph:
    def __init__(self, config: Union[Path, ocio.Config]):

        self.config: ocio.Config
        if isinstance(config, Path):
            self.config = ocio.Config().CreateFromFile(str(config))
        else:
            self.config = config

        self.target_display = None
        self.target_view = None
        self.target_look: ocio.Look = None

    def get_proc(self):

        return
