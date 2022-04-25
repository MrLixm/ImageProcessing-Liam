"""
python>3.6
"""
import logging
import re
from glob import glob
from pathlib import Path
from pprint import pprint
from typing import List

from PIL import Image

import imageGridCombine as iGC

__all__ = ["get_specific_files_from_dir", "extract_crop_data", "combine_from_nuke"]

logger = logging.getLogger("iGC.utilities")


def get_specific_files_from_dir(
    directory: Path,
    extension: str,
    regex: str,
) -> List[Path]:
    """
    From given directory return files inside matching the given parameter.
    Only work at first depth level.

    Args:
        directory:
        extension: file format extension without the delimitter (dot)
        regex: regulax expression pattern that each path must match to

    Returns:

    """
    pattern = re.compile(regex)
    sources_list: List[str] = glob(str(directory / f"*.{extension}"))
    sources_list = list(filter(lambda fp: pattern.search(fp), sources_list))
    sources_list: List[Path] = list(map(lambda fp: Path(fp), sources_list))
    return sources_list


def extract_crop_data(filepath: Path):
    """

    Args:
        filepath: path with the crop information baked in the name

    Returns:
        crop information as (row, column)
    """

    crop_info = filepath.stem.split(".")[-1]
    column, row = crop_info.split("x")
    row = int(row)
    column = int(column)

    logger.debug(f"[extract_crop_data] {row},{column} found for {filepath}")
    return row, column


def combine_from_nuke(
    sources_list: List[Path],
) -> Image.Image:
    """

    Args:
        sources_list: list of file paths to combine

    Returns:
        combined image of all the images in sources_list
    """

    # Create a list of Image.Image and order it :
    images_list: List[iGC.ImageGridPart] = iGC.core.images_list_to_imagegridparts(
        images_list=sources_list, crop_data_function=extract_crop_data
    )

    grid_rows: List[int] = list(map(lambda igp: igp.row, images_list))
    grid_cols: List[int] = list(map(lambda igp: igp.column, images_list))
    grid_rows: int = max(grid_rows) + 1
    grid_cols: int = max(grid_cols) + 1

    images_list: List[Image.Image] = list(map(lambda igp: igp.image, images_list))

    # Create the Image grid
    img_grid = iGC.core.to_image_grid(images_list, grid_rows, grid_cols)

    logger.info(f"[combine_from_nuke] Finished.")
    return img_grid


def write_jpg(img: Image.Image, export_path: Path, **kwargs) -> Path:
    """

    Args:
        img: PIL image to export
        export_path: full path to write the file. Also drive which format should the
            spurce file must be encoded in.
        kwargs: additional argument passed to the save() method.

    Returns:
        path of the exported file

    """
    img.save(fp=export_path, quality=95, subsampling=0, **kwargs)  # 4:4:4
    logger.info(f"[write_jpg] Finish writing {export_path}.")
    return export_path


def __test():

    file_list = get_specific_files_from_dir(
        directory=Path(
            r"G:\personal\photo\workspace\outputs\08_00_2021_Meuse\cacahuete1"
        ),
        extension="jpg",
        regex=r".+\.0002\.(\d)+x(\d)+",
    )
    pprint(file_list, width=1)
    assert file_list, "No file found, check passed parameters or source directory."
    return


if __name__ == "__main__":
    __test()
