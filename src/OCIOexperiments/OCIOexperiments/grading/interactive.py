"""

"""
import logging
from dataclasses import dataclass
from typing import (
    Optional,
    Union,
    Dict,
    ClassVar,
    Tuple,
)

import PyOpenColorIO as ocio

import OCIOexperiments as ocex
from OCIOexperiments.vendor.PySignal import Signal
from . import c

__all__ = ("GradingInteractive",)


logger = logging.getLogger(f"{c.ABR}.ocioUtils")


# TODO :
"""
- refactor how this should behave depending of the grading mode
    - delete lift ? only expose common ? create on class per mode ?
- also trigger saturation when only exposure/gamma
"""


@dataclass
class GradingInteractive:
    """
    List of common grading transform to apply in an interactive context to an image.

    Call ``repr()`` to get a dict representation.

    You can connect the ``sgn_dynamicprops`` that will be emitted when any value
    associated to an OCIO dynamic property is modified.
    """

    exposure: float = 0.0
    gamma: float = 1.0

    # GradingPrimary
    contrast: Union[float, Tuple[float, float, float]] = 1.0
    lift: Union[float, Tuple[float, float, float]] = 0.0
    offset: Union[float, Tuple[float, float, float]] = 0.0
    pivot: float = 0.18
    saturation: float = 1.0

    grading_space = ocio.GRADING_LIN
    """
    Choose in which space must some of the interactive color grading operations are 
    performed. This will not affect *exposure* and *gamma* adjustements.

    For now the input image has to be encoded in the same format (so log transfer-function
    if ``GRADING_LOG``).

    Can be one of :

    - ocio.GRADING_LIN
    - ocio.GRADING_LOG
    - ocio.GRADING_VIDEO
    """

    _propconfig: ClassVar[Dict[str, ocio.DynamicPropertyType]] = {
        "exposure": (exposure, ocio.DYNAMIC_PROPERTY_EXPOSURE),
        "gamma": (gamma, ocio.DYNAMIC_PROPERTY_GAMMA),
        "contrast": (contrast, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY),
        "pivot": (pivot, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY),
        "lift": (lift, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY),
        "offset": (offset, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY),
        "saturation": (saturation, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY),
        "grading_space": (grading_space, ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY),
    }
    """
    | Dict of {*class attribute name*: *config tuple*, ...}.
    | Where *config tuple* = (*default value*, *associated dynamic prop*)
    """

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

    def __str__(self) -> str:
        return str(self.__repr__())

    def __setattr__(self, key, value):

        # emit which dynamic properties changed to update the OCIO processor upstream
        dp: Optional[tuple] = self._propconfig.get(key)
        if dp is not None:
            dp: ocio.DynamicPropertyType = dp[1]
            self.sgn_dynamicprops.emit(dp, value)

        super().__setattr__(key, value)
        return

    @classmethod
    def get_default(cls, name) -> float:
        """
        Returns:
            default value (producing a passthrough operation) for the given operation name
        """
        return cls._propconfig.get(name)[0]

    @property
    def is_default(self):
        # HACK saturation
        return (
            self._is_default_except_sat
            and self.saturation == self.get_default("saturation")
            and self.grading_space == self.get_default("grading_space")
        )

    @property
    def is_modified_sat_only(self):
        # HACK saturation :
        # https://github.com/AcademySoftwareFoundation/OpenColorIO/issues/1642
        return self._is_default_except_sat and self.saturation != self.get_default(
            "saturation"
        )

    @property
    def _is_default_except_sat(self):
        # HACK saturation :
        return (
            self.exposure == self.get_default("exposure")
            and self.contrast == self.get_default("contrast")
            and self.gamma == self.get_default("gamma")
            and self.pivot == self.get_default("pivot")
            and self.lift == self.get_default("lift")
            and self.offset == self.get_default("offset")
        )

    @property
    def grading_primary(self) -> ocio.GradingPrimary:

        gp = ocio.GradingPrimary(self.grading_space)

        # HACK: https://github.com/AcademySoftwareFoundation/OpenColorIO/issues/1643
        if isinstance(self.contrast, tuple):
            contrast = tuple(map(lambda f: f * 0.999999, self.contrast))
        else:
            contrast = self.contrast

        gp.contrast = ocex.wrappers.to_rgbm(contrast, "*")
        gp.lift = ocex.wrappers.to_rgbm(self.lift)
        gp.offset = ocex.wrappers.to_rgbm(self.offset, "+")
        gp.pivot = self.pivot
        gp.saturation = self.saturation

        # HACK saturation :
        # https://github.com/AcademySoftwareFoundation/OpenColorIO/issues/1642
        if self.is_modified_sat_only:
            gp.clampBlack = -150

        return gp

    def update_all_shader_dyn_prop(self, shader: ocio.GpuShaderDesc):

        for classattribute, data in self._propconfig.items():
            _, dynamicprop = data
            v = self.__getattribute__(classattribute)
            ocex.utils.update_shader_dyn_prop(
                shader=shader, prop_type=dynamicprop, value=v
            )

        return
