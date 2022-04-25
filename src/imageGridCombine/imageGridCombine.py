"""
python>3.6
"""
from glob import glob
import os
from pathlib import Path
from typing import Set, List

from PIL import Image

__all__ = ["ImageGridPart", "to_image_grid"]


def run():

    # 1. Get a list of image to process
    # ----------------------------------
    export_version = "0002"

    source_dir = Path(
        r"G:\personal\photo\workspace\outputs\08_00_2021_Meuse\cacahuete1"
    ).resolve()
    # parse directory to find the desired files
    sources_list: List[str] = glob(str(source_dir / "*?x?.jpg"))
    # keep only the file with the specified version
    sources_list: List[str] = list(
        filter(lambda p: export_version in Path(p).stem, sources_list)
    )

    assert sources_list, f"No images found to process in {source_dir} !"

    _debug = "\n".join([f"    - {fp}" for fp in sources_list])
    print(f"[{__name__}][run] Found {len(sources_list)} images to combine :\n{_debug}")

    # 2. Create a list of Image.Image and order it
    # --------------------------------------------
    sources_rows = 0
    sources_columns = 0
    images_list: List[ImageGridPart] = list()

    for img_path in sources_list:

        img_path = Path(img_path)
        img = Image.open(img_path)

        # determine the number of row and column from the file name
        crop_info = img_path.stem.split(".")[-1]
        column, row = crop_info.split("x")
        column = int(column)
        row = int(row)
        sources_columns = column if column > sources_columns else sources_columns
        sources_rows = row if row > sources_rows else sources_rows

        img = ImageGridPart(column=column, row=row, img=img)
        images_list.append(img)

        continue

    sources_rows += 1
    sources_columns += 1
    images_list.sort()
    images_list.reverse()
    images_list: List[Image.Image] = list(map(lambda igp: igp.image, images_list))

    # 3. Create the Image grid and save it
    # ------------------------------------
    img_grid = to_image_grid(images_list, sources_rows, sources_columns)

    target_path = source_dir / f"combined.{export_version}.jpg"
    img_grid.save(
        fp=target_path,
        exif=images_list[0].getexif(),
        quality=95,
        subsampling=0,  # 4:4:4
    )
    print(f"[{__name__}][run] Wrote {target_path}.")

    print(f"[{__name__}][run] Finished.")
    return


"""=====================================================================================

    API

"""


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
    assert (
        len(imgs) == rows * cols
    ), f"Incorrect number of Images passed. Expected {rows * cols}, got {len(imgs)}."

    # 1. Find the output image size by adding all the image width/height
    grid_width = 0
    grid_height = 0
    for img in imgs:
        grid_width += img.size[0]
        grid_height += img.size[1]
    grid_width = grid_width / rows
    grid_height = grid_height / cols
    print(
        f"[{__name__}][to_image_grid] Creating image of size [{grid_width}]x[{grid_height}]"
    )

    # 2. Create the output image
    img_grid = Image.new("RGB", size=(int(grid_width), int(grid_height)))

    topleftcorner_x = 0
    topleftcorner_y = 0

    for i, img in enumerate(imgs):

        col = i % cols
        "starts at 0"
        row = i // cols
        "starts at 0"

        w, h = img.size

        print(
            f"[{__name__}][to_image_grid] {i} img[{img.size[0]} x {img.size[1]}] :"
            f" row[{row}] col[{col}] :"
            f" xy({topleftcorner_x}, {topleftcorner_y})"
        )
        img_grid.paste(img, box=(int(topleftcorner_x), int(topleftcorner_y)))

        topleftcorner_x = 0 if col == cols - 1 else topleftcorner_x + w
        topleftcorner_y = topleftcorner_y if col != cols - 1 else topleftcorner_y + h
        continue

    print(f"[{__name__}][to_image_grid] Finished processing grid image {rows}x{cols}")
    return img_grid


if __name__ == "__main__":
    run()
