"""

"""
import logging
from pathlib import Path
from typing import (
    Optional,
    Union,
)

import PyOpenColorIO as ocio

from . import c
from .interactive import GradingInteractive

__all__ = ("OcioOperationGraph",)


logger = logging.getLogger(f"{c.ABR}.processes")


class OcioOperationGraph:
    """
    Describe color operations to perform on an image that has just been decoded from disk.
    The whole pipeline is described as:

    ``input-> working space -> grading -> display``

    The workspace colorspace is assumed to be the role ``SCENE_LINEAR`` by default but
    can be changed. If "log-flavored" you could for example set
    <GradingInteractive> grading_space to <ocio.GRADING_LOG> to adapat grading operation
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
        Specify the colorspace in which the input is encoded to be converted to 
        the workspace colorspace.
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
            {self.grading}

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

        # TODO check if "IF" necessary as OCIO might already applied optimisation in the proc
        if not self.grading.is_default:

            for trsfm in self.grading.as_transforms():
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
