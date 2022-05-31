"""

"""
import logging
from dataclasses import dataclass
from typing import (
    Optional,
    Dict,
    ClassVar,
    List,
)

import PyOpenColorIO as ocio

import OCIOexperiments as ocex
from OCIOexperiments.vendor.PySignal import Signal
from . import c

__all__ = ("GradingInteractive",)


logger = logging.getLogger(f"{c.ABR}.interactive")


@dataclass
class GradingInteractive:
    """
    Common grading transforms to apply in an interactive context to an image.
    This doesn't apply any processing but just store values to apply.


    In terms of public objects :

    -
        Call ``repr()`` to get a dict representation of the grading values.

    -
        You can connect the ``sgn_dynamicprops`` that will be emitted when any value
        associated to an OCIO dynamic property is modified.

    -
        the ``transforms`` property is the final target

    -
        ``update_all_shader_dyn_prop`` can be used in a GPU context for OCIO to update
        the shader dynamic properties.
    """

    exposure: float = 0.0
    gamma: float = 1.0
    # GradingPrimary
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
        "exposure": (exposure, ocio.DYNAMIC_PROPERTY_EXPOSURE, None),
        "gamma": (gamma, ocio.DYNAMIC_PROPERTY_GAMMA, None),
        "saturation": (
            saturation,
            ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY,
            "_grading_primary",
        ),
        "grading_space": (
            grading_space,
            ocio.DYNAMIC_PROPERTY_GRADING_PRIMARY,
            "_grading_primary",
        ),
    }
    """
    | Dict of {``class attribute name``: ``config tuple``, ...}.
    | Where ``config tuple`` = (
        "default value",
        "associated dynamic prop",
        "dynamic prop value to send, a class attribute name too")
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
            "saturation": self.saturation,
        }

    def __str__(self) -> str:
        return str(self.__repr__())

    def __setattr__(self, key, value):
        """
        Change one of the class attribute. If this attribute corresponds to a
        dynamic property, this one will be emitted in the ``sgn_dynamicprops`` signal.
        """

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
        return self._is_default_except_sat and self.saturation == self.get_default(
            "saturation"
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
        return self.exposure == self.get_default(
            "exposure"
        ) and self.gamma == self.get_default("gamma")

    @property
    def _grading_primary(self) -> ocio.GradingPrimary:
        """
        Convert the grading operations that in terms of OCIO API corresponds
        the GradingPrimary class.
        """

        gp = ocio.GradingPrimary(self.grading_space)
        gp.saturation = self.saturation

        # HACK saturation :
        # https://github.com/AcademySoftwareFoundation/OpenColorIO/issues/1642
        if self.saturation != self.get_default("saturation"):
            gp.clampBlack = -150

        return gp

    def as_transforms(self, dynamic: bool = True) -> List[ocio.Transform]:
        """
        Convert this class to OCIO API by returning a corresponding list of OCIO
        transforms to apply.

        Args:
            dynamic: are transforms properties dynamic

        Returns:
            list of OCIO transform to apply in the same order.
        """

        trsfm_list = list()

        trsfm = ocio.GradingPrimaryTransform(
            self._grading_primary,
            self.grading_space,
            dynamic,
        )
        trsfm_list.append(trsfm)

        trsfm = ocio.ExposureContrastTransform(
            exposure=self.exposure,
            dynamicExposure=dynamic,
        )
        trsfm_list.append(trsfm)

        # TODO check pivot
        trsfm = ocio.ExposureContrastTransform(
            gamma=self.gamma,
            pivot=0.18,
            dynamicGamma=dynamic,
        )
        trsfm_list.append(trsfm)

        return trsfm_list

    def update_all_shader_dyn_prop(self, shader: ocio.GpuShaderDesc):

        for classattribute, data in self._propconfig.items():
            _, dynamicprop, dynamicprop_value = data
            v = self.__getattribute__(
                classattribute if dynamicprop_value is None else dynamicprop_value
            )
            ocex.utils.update_shader_dyn_prop(
                shader=shader, prop_type=dynamicprop, value=v
            )

        return
