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

import OCIOexperiments as ocex
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
            update_shader_dyn_prop(shader=shader, prop_type=dynamicprop, value=v)

        return


class OcioOperationGraph:
    """
    Describe color operations to perform on an image that has just been decoded from disk.
    The whole pipeline is described: ``input-> working space -> grading -> display``.

    The workspace colorspace is assumed to be the role SCENE_LINEAR by default but can
    be changed. It can be "log-flavored" so you could for example set
    <GradingInteractive> grading_space to <ocio.GRADING_LOG>
    """

    def __init__(self, config: Union[Path, ocio.Config]):

        self._config: ocio.Config
        if isinstance(config, Path):
            self._config = ocio.Config().CreateFromFile(str(config))
        else:
            self._config = config

        self._config.validate()

        self.input_encoding: str = None
        """
        Also called IDT. 
        Conversion to perform to convert the input image to the workspace colorspace.
        """

        self.workspace_colorspace: str = ocio.ROLE_SCENE_LINEAR
        """
        Interchange colorspace for all operations.
        """

        self.grading: GradingInteractive = GradingInteractive()
        """
        An interactive grading operation to perform on the open-domain data before
        the display conversion.
        """

        # to Display conversions
        self.target_display: str = None
        self.target_view: str = None
        self.target_looks: Optional[str] = None
        """
        List of Looks to apply following the OCIO conventions :
        
        Potential comma (or colon) delimited list of look names,
        where +/- prefixes are optionally allowed to denote forward/inverse look
        specification. (And forward is assumed in the absence of either).
        """

    def __str__(self) -> str:
        """
        Returns:
            a string representing the order of operation and their value used.
            Useful for debugging.
        """

        return f"""
        
        ColorSpaceTransform:
            from: {self.input_encoding}
            to: {self.workspace_colorspace}
        
        Grading:
            ignored ? (=default): {self.grading.is_default}
            GradingPrimaryTransform:
                gp: {self.grading.grading_primary}
                space: {self.grading.grading_space}
            ExposureContrastTransform:
                exposure: {self.grading.exposure}
                gamma: {self.grading.gamma}
        
        Looks:
            {self.target_looks}
        
        DisplayViewTransform;
            src: {self.workspace_colorspace},
            display: {self.target_display},
            view: {self.target_view},
        """

    def get_proc(self) -> ocio.Processor:

        self.validate()

        grptransform = ocio.GroupTransform()
        "master transform used to generate the processor"

        trsfm = ocio.ColorSpaceTransform(
            src=self.input_encoding,
            dst=self.workspace_colorspace,
        )
        grptransform.appendTransform(trsfm)

        # TODO check if necessary as OCIO might already applied optimisation in the proc
        if not self.grading.is_default:

            trsfm = ocio.GradingPrimaryTransform(
                self.grading.grading_primary,
                self.grading.grading_space,
                True,
            )
            grptransform.appendTransform(trsfm)

            trsfm = ocio.ExposureContrastTransform(
                exposure=self.grading.exposure,
                dynamicExposure=True,
            )
            grptransform.appendTransform(trsfm)

            # TODO check pivot
            trsfm = ocio.ExposureContrastTransform(
                gamma=self.grading.gamma,
                pivot=0.18,
                dynamicGamma=True,
            )
            grptransform.appendTransform(trsfm)

        if self.target_looks:
            trsfm = ocio.LookTransform()
            trsfm.setSrc(self.workspace_colorspace)
            trsfm.setDst(self.workspace_colorspace)
            trsfm.setLooks(self.target_looks)
            grptransform.appendTransform(trsfm)

        trsfm = ocio.DisplayViewTransform(
            src=self.workspace_colorspace,
            display=self.target_display,
            view=self.target_view,
        )
        grptransform.appendTransform(trsfm)

        return self._config.getProcessor(grptransform)

    def validate(self):
        """
        Raises:
            AssertionError: if this instance is malformed.
        """
        assert self.input_encoding, "Missing input_encoding colorspace."
        assert self.target_display, "Missing target_display."
        assert self.target_view, "Missing target_view."

        assert self._config.getColorSpace(
            self.input_encoding
        ), f"Can't find input colorspace <{self.input_encoding}>"

        assert (
            self.target_display in self._config.getDisplays()
        ), f"Can't find target display <{self.target_display}>."

        assert self.target_view in self._config.getViews(
            self.target_display
        ), f"Can't find target view <{self.target_view}>."

        return
