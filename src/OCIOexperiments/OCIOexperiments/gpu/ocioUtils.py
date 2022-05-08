"""

"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Optional,
    Union,
    Dict,
    ClassVar,
    Tuple,
)

import PyOpenColorIO as ocio

from . import c
from .PySignal import Signal

__all__ = (
    "update_shader_dyn_prop",
    "GradingInteractive",
    "OcioOperationGraph",
)


logger = logging.getLogger(f"{c.ABR}.ocioUtils")


def update_shader_dyn_prop(
    shader: ocio.GpuShaderDesc,
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

    if shader.hasDynamicProperty(prop_type):
        dyn_prop: ocio.DynamicProperty = shader.getDynamicProperty(prop_type)
        dyn_prop.setDouble(value)
        return dyn_prop


def to_rgbm_ocio(value: Union[float, Tuple[float, float, float]]) -> ocio.GradingRGBM:
    """
    Convert a python object to an OCIO GradingRGBM instance to use for GradingPrimary.

    Args:
        value: a value to apply on all channel or one different per-channel (RGB)

    Returns:
        GradingRGBM instance
    """

    grgbm = ocio.GradingRGBM()
    if isinstance(value, float):
        grgbm.master = value
    else:
        grgbm.red = value[0]
        grgbm.green = value[1]
        grgbm.blue = value[2]

    return grgbm


@dataclass
class GradingInteractive:
    """
    List of common grading transform to apply in an interactive context to an image.

    Call ``repr()`` to get a dict representation.

    You can connect the ``sgn_dynamicprops`` that will be emitted when any value
    associated to an OCIO dynamic property is modified.
    """

    exposure: float = 1.0
    gamma: float = 1.0

    # GradingPrimary
    contrast: Union[float, Tuple[float, float, float]] = 0.0
    lift: Union[float, Tuple[float, float, float]] = 0.0
    offset: Union[float, Tuple[float, float, float]] = 0.0
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

    _dynamicprops: ClassVar[Dict[str, ocio.DynamicPropertyType]] = {
        "exposure": ocio.DYNAMIC_PROPERTY_EXPOSURE,
        "gamma": ocio.DYNAMIC_PROPERTY_GAMMA,
        "contrast": ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY,
        "pivot": ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY,
        "saturation": ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY,
        "grading_space": ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY,
    }

    sgn_dynamicprops: ClassVar[Signal] = Signal()
    """
    | Emitted when any grading value is changed and is associated to an
     OCIO dynamic property.
    | Emit ``Tuple[dynamicproperty: ocio.DynamicPropertyType, value:Any]``
    """

    def __repr__(self) -> dict:
        return {
            "exposure": self.exposure,
            "gamma": self.gamma,
            "grading_space": str(self.grading_space),
            "contrast": self.contrast,
            "pivot": self.pivot,
            "saturation": self.saturation,
        }

    def __setattr__(self, key, value):

        # emit which dynamic properties changed to update the OCIO processor upstream
        dp = self._dynamicprops.get(key)
        if dp is not None:
            self.sgn_dynamicprops.emit(dp, value)

        super().__setattr__(key, value)
        return

    @property
    def grading_primary(self) -> ocio.GradingPrimary:

        gp = ocio.GradingPrimary(self.grading_space)

        gp.contrast = to_rgbm_ocio(self.contrast)
        gp.lift = to_rgbm_ocio(self.lift)
        gp.offset = to_rgbm_ocio(self.offset)
        gp.pivot = self.pivot
        gp.saturation = self.saturation
        return gp

    def update_all_shader_dyn_prop(self, shader: ocio.GpuShaderDesc):

        for classattribute, dynamicprop in self._dynamicprops.items():

            v = self.__getattribute__(classattribute)
            update_shader_dyn_prop(shader=shader, prop_type=dynamicprop, value=v)

        return


class OcioOperationGraph:
    def __init__(self, config: Union[Path, ocio.Config]):

        self.config: ocio.Config
        if isinstance(config, Path):
            self.config = ocio.Config().CreateFromFile(str(config))
        else:
            self.config = config

        self.grading: GradingInteractive = GradingInteractive()
        """
        An interactive grading operation to perform on the open-domain data before
        the display conversion.
        """

        self.target_display = None
        self.target_view = None
        self.target_look: ocio.Look = None

    # TODO
    def get_proc(self) -> ocio.Processor:

        pass
