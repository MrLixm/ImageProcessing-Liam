"""
author=Liam Collod
last_modified=26/04/2022
python>3.6

[LICENSE]
Copyright 2022 Liam Collod
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import logging
from pathlib import Path
from typing import List, Callable, Tuple, TypeVar

from PIL import Image

__all__ = ["ImageGridPart", "ImageGrid", "to_image_grid", "paths_to_imagegridparts"]

logger = logging.getLogger("iGC.core")

ImgType = TypeVar("ImgType")


class ImageGridPart(tuple):
    """
    Convenient class to describe a part of an image stored into multiple crops.
    Subclassing tuple to change its behavior.

    Each crop is represented by its column and row number which both starts at 0.

    Crop "order" use `PIL.Image` order, i.e. starting from the upper
    left-corner (column=0, row=0) and going to the bottom-right corner.
    """

    def __new__(cls, column: int, row: int, img: ImgType):
        return super(ImageGridPart, cls).__new__(cls, (column, row, img))

    def __init__(self, column: int, row: int, img: ImgType):
        pass

    def __gt__(self, other) -> bool:
        # >
        if self.row == other.row:
            return self.column < other.column
        else:
            return self.row < other.row

    def __lt__(self, other) -> bool:
        # <
        return not self.__gt__(other)

    def __le__(self, other) -> bool:
        # <=
        return self.__lt__(other) or (
            other.row == self.row and other.column == self.column
        )

    def __ge__(self, other) -> bool:
        # >=
        return self.__gt__(other) or (
            other.row == self.row and other.column == self.column
        )

    def __eq__(self, other) -> bool:
        # ==
        return (
            other.row == self.row
            and other.column == self.column
            and other.image == self.image
        )

    def __ne__(self, other) -> bool:
        # !=
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"col[{self.column}]row[{self.row}] ; img={self.image}"

    @property
    def column(self) -> int:
        return self.__getitem__(0)

    @property
    def row(self) -> int:
        return self.__getitem__(1)

    @property
    def image(self) -> ImgType:
        return self.__getitem__(2)


class ImageGrid:
    """
    Describe a "grid" image which is multiple images append together in
    a row/column format.

    Images are appended to the final composite from left to right and top to bottom
    which mean starting from row0-column0, then row0-column1, ...
    You can use `reverse_rows()` or `reverse_columns()` if your crops were using
    the inverse order.

    Attributes:
        parts: list of ImagineGridParts to combine to a single image
        image: combined image
        grid_rows: number of rows in the grid (starts at 1)
        grid_cols: number of columns in the grid (starts at 1)

    """

    def __init__(self, parts: List[ImageGridPart]):

        self.parts: List[ImageGridPart] = parts
        self.image: Image.Image = None
        self.grid_rows: int = 0
        self.grid_cols: int = 0

        self.build()
        return

    def build(self):

        self.grid_rows: List[int] = list(map(lambda igp: igp.row, self.parts))
        self.grid_cols: List[int] = list(map(lambda igp: igp.column, self.parts))
        self.grid_rows: int = max(self.grid_rows) + 1
        self.grid_cols: int = max(self.grid_cols) + 1

        images_list: List[ImgType] = list(map(lambda igp: igp.image, self.parts))

        self.image: Image.Image = to_image_grid(
            imgs=images_list, rows=self.grid_rows, cols=self.grid_cols
        )
        logger.debug(f"[{self.__class__.__name__}][build] Finished")
        return

    def reverse_columns(self):
        """
        For all ImageGridPart, inverse the column index, so the last index become the first.
        Exemple for a 4 column grid : 4->0, 3->1, ...
        """
        for i, igp in enumerate(self.parts):
            ncol = self.grid_cols - 1 - igp.column
            self.parts[i] = ImageGridPart(ncol, igp.row, igp.image)
        logger.debug(
            f"[{self.__class__.__name__}][reverse_columns] Finished. Calling build() ..."
        )
        self.parts.sort()
        self.parts.reverse()
        self.build()
        return

    def reverse_rows(self):
        """
        For all ImageGridPart, inverse the row index, so the last index become the first.
        Exemple for a 3 row grid : 3->0, 2->1, 1->0
        """
        for i, igp in enumerate(self.parts):
            nrow = self.grid_rows - 1 - igp.row
            self.parts[i] = ImageGridPart(igp.column, nrow, igp.image)
        logger.debug(
            f"[{self.__class__.__name__}][reverse_rows] Finished. Calling build() ..."
        )
        self.parts.sort()
        self.parts.reverse()
        self.build()
        return

    def write_to(self, export_path: Path, **kwargs):
        """

        Args:
            export_path:  full path to write the file. Also drive which format should
                the grid image must be encoded in.
            **kwargs: additional argument passed to the save() method.

        """

        if export_path.suffix == ".jpg":
            self.image = self.image.convert(mode="RGB")
            self.image.save(fp=export_path, **kwargs)
        else:
            raise ValueError(
                f"Unsuported extension {export_path.suffix} from {export_path}"
            )

        logger.info(
            f"[{self.__class__.__name__}][write_to] Finish writing {export_path}."
        )
        return

    @classmethod
    def build_from_paths(
        cls,
        paths_list: List[Path],
        crop_data_function: Callable[[Path], Tuple[int, int]],
    ):
        """

        Args:
            paths_list:
            crop_data_function: function that return (row, column) from a path.

        Returns:
            given images path as a combined ImageGrid object.
        """
        parts = paths_to_imagegridparts(paths_list, crop_data_function)
        return ImageGrid(parts=parts)


def paths_to_imagegridparts(
    paths_list: List[Path], crop_data_function: Callable[[Path], Tuple[int, int]]
) -> List[ImageGridPart]:
    """
    Convert a filepath to an ImageGridPart instance. A callable must be passed that
    will return which row and column the filepath correspond to.

    Args:
        paths_list:
        crop_data_function: function that return (row, column) from a path.
            type hint:  Callable[[Path], Tuple[int, int]]

    Returns:
        given images path as PIL images with their associated row/column index.
    """

    out: List[ImageGridPart] = list()

    for img_path in paths_list:

        # determine the number of row and column from the file name
        row, column = crop_data_function(img_path)

        img = Image.open(img_path)
        img = ImageGridPart(column=column, row=row, img=img)
        out.append(img)

        continue

    out.sort()
    out.reverse()

    logger.info(
        f"[paths_to_imagegridparts] Finished converting {len(paths_list)} images."
    )
    return out


def to_image_grid(imgs: list[Image.Image], rows: int, cols: int) -> Image.Image:
    """
    The real core function of all this module.
    Based on : https://stackoverflow.com/a/65583584/13806195

    Behavior hardocoded to PIL processing from top left corner to bottom right corner

    Args:
        imgs: list is expected to be already ordered in the PIL order. I.e. starting from
            the upper left corner and going from left to right.
        rows:
        cols:

    Returns:
        combined version of all the passed images
    """
    assert len(imgs) == rows * cols, (
        f" [to_image_grid] Incorrect number of Images passed. Expected {rows * cols},"
        f" got {len(imgs)}."
    )

    # 1. Find the output image size by adding all the image width/height
    grid_width = 0
    grid_height = 0
    for img in imgs:
        grid_width += img.size[0]
        grid_height += img.size[1]
    grid_width = grid_width / rows
    grid_height = grid_height / cols
    logger.info(
        f"[to_image_grid] Creating image of size [{grid_width}]x[{grid_height}]"
    )

    # 2. Create the output image
    img_grid = Image.new("RGBA", size=(int(grid_width), int(grid_height)))

    topleftcorner_x = 0
    topleftcorner_y = 0

    for i, img in enumerate(imgs):

        # both starts at 0
        col = i % cols
        row = i // cols

        w, h = img.size

        logger.debug(
            f"[to_image_grid] {i} img[{img.size[0]} x {img.size[1]}] :"
            f" col[{col}] row[{row}] : xy({topleftcorner_x}, {topleftcorner_y})"
        )
        img_grid.paste(img, box=(int(topleftcorner_x), int(topleftcorner_y)))

        topleftcorner_x = 0 if col == cols - 1 else topleftcorner_x + w
        topleftcorner_y = topleftcorner_y if col != cols - 1 else topleftcorner_y + h
        continue

    logger.info(f"[to_image_grid] Finished processing grid image {rows}x{cols}")
    return img_grid
