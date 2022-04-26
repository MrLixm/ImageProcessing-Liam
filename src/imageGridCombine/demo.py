"""
author=Liam Collod
last_modified=26/04/2022
python>3.6

[What]

Exemple file of how you could use iGC.
Logging need to be setup before executing any function.

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
import sys
from pathlib import Path
from typing import Tuple

import imageGridCombine as iGC


def setup_logging(level: str):
    """
    Add some formatter/handler for the logegr using "iGC"
    """

    logger = logging.getLogger("iGC")
    logger.setLevel(level)

    if not logger.handlers:
        # create a file handler
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        handlerfile = logging.FileHandler(Path(".log"))
        # create a logging format
        formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)7s] %(name)30s // %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        handlerfile.setFormatter(formatter)
        # add the file handler to the logger
        logger.addHandler(handler)
        logger.addHandler(handlerfile)

    return


def extract_crop_data_custom(filepath: Path) -> Tuple[int, int]:
    # here, it just returns a premade function that fit to my needs, but you
    # could do anything here to extract the crop data from the filepath.
    # As long as the row is returned first , then the column index.
    return iGC.utilities.extract_crop_data(filepath=filepath)


def run(source_dir: Path, sources_version: str):

    # 1. Find all image that need to be combined
    extension = "jpg"
    regex = rf".+\.{sources_version}\.(\d)+x(\d)+"

    target_path = Path(f"demo.{sources_version}.{extension}")

    sources_list = iGC.utilities.get_specific_files_from_dir(
        directory=source_dir,
        extension=extension,
        regex=regex,
    )

    assert sources_list, f"No file found in directory {source_dir}"

    _ = "\n".join([f"    - {fp}" for fp in sources_list])
    print(f"Found {len(sources_list)} images to combine :\n{_}")

    # 2. Combine those images
    imggrid = iGC.ImageGrid.build_from_paths(
        paths_list=sources_list,
        crop_data_function=extract_crop_data_custom,
    )
    imggrid.reverse_rows()
    imggrid.write_to(export_path=target_path, quality=95, subsampling=0)

    assert target_path.exists(), f"Target {target_path} doesn't exists on disk !"

    print("[run] Finished.")
    return


if __name__ == "__main__":

    setup_logging(logging.DEBUG)

    run(
        source_dir=Path(r"./imageGridCombine/tests/img/test1"),
        sources_version="0001",
    )
