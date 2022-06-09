"""

"""
import logging
from pathlib import Path
from typing import Optional, Union

from Qt import QtOpenGL
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
import PyOpenColorIO as ocio

from . import c
import OCIOexperiments as ocex
from OCIOexperiments import grading
from OCIOexperiments import gpu
import lxmImageIO

logger = logging.getLogger(f"{c.ABR}.basicViewer")

CONFIGTEMP = ocio.Config().CreateFromFile(
    str(ocex.c.DATA_DIR / "configs" / "AgXc-v0.1.4" / "config.ocio")
)


class ImageGlWidget(QtOpenGL.QGLWidget, gpu.GLImage):
    def __init__(self, parent=None):

        QtOpenGL.QGLWidget.__init__(self, parent)
        gpu.GLImage.__init__(self)

        self.init_ui()
        return

    def init_ui(self):

        self.update_sgn.connect(self.update)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding,
            )
        )

        return

    def initializeGL(self):
        gpu.GLImage.initializeGL(self)

    def resizeGL(self, w, h):
        gpu.GLImage.resizeGL(self, w, h)

    def paintGL(self):
        gpu.GLImage.paintGL(self)


class BasicImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):

        # // CREATE
        self.glimage = ImageGlWidget(self)
        self.lyt = QtWidgets.QVBoxLayout()

        # // MODIFY
        self.resize(QtCore.QSize(1280, 720))
        self.lyt.setContentsMargins(0, 0, 0, 0)
        self.lyt.setSpacing(0)

        # // SETUP LAYOUTS
        self.setLayout(self.lyt)
        self.lyt.addWidget(self.glimage)

        # // SETUP CONNECTIONS
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+o"), self)
        shortcut.activated.connect(self.load_image)
        return

    def load_image(self, path: Optional[Union[Path, str]] = None):

        path = path or self.open_file_browser()
        if not path:
            logger.warning(
                f"[{self.__class__.__name__}][load_image] Aborted. No path provided."
            )
            return

        image: lxmImageIO.containers.ImageContainer
        image = lxmImageIO.io.read.readToImage(source=Path(path), colorspace=None)
        self.glimage.load(image=image)
        logger.info(f"[{self.__class__.__name__}][load_image] Loaded image {path}")
        return

    def open_file_browser(self) -> Optional[str]:
        """
        Opens a file browser window to select a single image file.

        Returns:
            path of the file selected or None
        """
        image_path, sel_filter = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load an Image",
        )
        return image_path
