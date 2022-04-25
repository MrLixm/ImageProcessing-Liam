"""
python>3.6
"""
import logging
from pathlib import Path
from typing import List, Callable, Tuple

from PIL import Image

__all__ = ["ImageGridPart", "to_image_grid", "images_list_to_imagegridparts"]

logger = logging.getLogger("iGC.imageGridCombine")


class ImageGridPart(tuple):
    """
    Convenient class to describe an image stored into multiple crops.
    Each crop is represented by its column and row number.
    Each crop importance use PIL.Image order, i.e. starting from the upper
    left-corner (column=0, row=max(rox))
    """

    def __new__(cls, column: int, row: int, img: Image.Image):
        return super(ImageGridPart, cls).__new__(cls, (column, row, img))

    def __init__(self, column: int, row: int, img: Image.Image):
        pass

    def __gt__(self, other) -> bool:
        # >
        if self.row == other.row:
            return self.column < other.column
        else:
            return self.row > other.row

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
    def image(self) -> Image.Image:
        return self.__getitem__(2)


def images_list_to_imagegridparts(
    images_list: List[Path], crop_data_function: Callable[[Path], Tuple[int, int]]
) -> List[ImageGridPart]:
    """

    Args:
        images_list:
        crop_data_function: function that return (row, column) from a path.

    Returns:
        given images path as PIL images with their associated row/column index.
    """

    out: List[ImageGridPart] = list()

    for img_path in images_list:

        # determine the number of row and column from the file name
        row, column = crop_data_function(img_path)

        img = Image.open(img_path)
        img = ImageGridPart(column=column, row=row, img=img)
        out.append(img)

        continue

    out.sort()
    out.reverse()

    logger.info(
        f"[images_list_to_imagegridparts] Finished converting {len(images_list)} images."
    )
    return out


def to_image_grid(imgs: list[Image.Image], rows: int, cols: int) -> Image.Image:
    """
    Based on : https://stackoverflow.com/a/65583584/13806195
    Alpha is ignored.
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
    img_grid = Image.new("RGB", size=(int(grid_width), int(grid_height)))

    topleftcorner_x = 0
    topleftcorner_y = 0

    for i, img in enumerate(imgs):

        # both starts at 0
        col = i % cols
        row = i // cols

        w, h = img.size

        logger.debug(
            f"[to_image_grid] {i} img[{img.size[0]} x {img.size[1]}] :"
            f" row[{row}] col[{col}] : xy({topleftcorner_x}, {topleftcorner_y})"
        )
        img_grid.paste(img, box=(int(topleftcorner_x), int(topleftcorner_y)))

        topleftcorner_x = 0 if col == cols - 1 else topleftcorner_x + w
        topleftcorner_y = topleftcorner_y if col != cols - 1 else topleftcorner_y + h
        continue

    logger.info(f"[to_image_grid] Finished processing grid image {rows}x{cols}")
    return img_grid
