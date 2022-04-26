"""
python>3.6
"""
import logging
import re
from glob import glob
from pathlib import Path
from pprint import pprint
from typing import List


__all__ = ["get_specific_files_from_dir", "extract_crop_data"]

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
