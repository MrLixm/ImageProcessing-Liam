"""

"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class TestImage:
    """
    A single disk file representing an image with a specific naming convention.
    """

    parent: TestAsset
    relative_path: Path
    """
    Path relative to given parent
    """

    def __post_init__(self):

        self._name_splitted = self.relative_path.stem.split(".")
        self.validate()

    @property
    def path(self):
        """
        Absolute path on disk.
        """
        return self.parent.path / self.relative_path

    @property
    def id(self) -> str:
        """
        Starts at one, 4 digit padding.
        """
        return self._name_splitted[1]

    @property
    def variant(self) -> str:
        return self._name_splitted[2]

    @property
    def colorspace(self) -> str:
        return self._name_splitted[3]

    @property
    def size(self) -> str:
        return self._name_splitted[4]

    @property
    def frame(self) -> str:
        return self._name_splitted[5]

    @property
    def ext(self) -> str:
        """
        File extension with the dot
        """
        return self.relative_path.suffix

    def validate(self):

        name = self.relative_path.stem
        check = name.count(".")
        assert check == 5, f"Invalid number of dot in {name} : expected 5 got {check}"

        check = re.match(r"\d\d\d\d", self.id)
        assert check, f"Invalid property <id> in {name} : expected 4 digits like 0012"
        return


class TestAsset:
    """
    An asset is a directory with TestImage inside.
    """

    def __init__(self, path: Path):
        self.path = path
        self.id = path.name  # directory name
        self.validate()

    @property
    def all(self) -> List[TestImage]:
        """
        Returns:
            All TestImage contains in the directory.
        """
        return [
            TestImage(relative_path=p.relative_to(self.path), parent=self)
            for p in self.path.iterdir()
            if p.is_file()
        ]

    @property
    def first(self) -> TestImage:
        """
        Returns:
            The testImage with the id 0001. Always present.
        """
        return [ti for ti in self.all if ti.id == "0001"][0]

    def get(
        self,
        variant: str = None,
        colorspace: str = None,
        size: str = None,
        frame: str = None,
        extension: str = None,
    ) -> Optional[TestImage]:
        """
        Return the first image which corresponds to the given parameters.
        (Even if too few paramaters are given to return only one image for sure).
        None if no correspondance found.

        Args:
            extension:
            variant:
            colorspace:
            size:
            frame:

        Returns:

        """
        out = self.all
        if variant:
            out = [ti for ti in out if ti.variant == variant]
        if colorspace:
            out = [ti for ti in out if ti.colorspace == colorspace]
        if size:
            out = [ti for ti in out if ti.size == size]
        if frame:
            out = [ti for ti in out if ti.frame == frame]
        if extension:
            out = [ti for ti in out if ti.ext == extension]

        return out[0] if out else None

    def validate(self):

        check = re.match(r"[^a-zA-Z\d_-]", self.id)
        assert not check, f"Invalid name used for directory <{self.id}>."

        assert self.all, f"No TestImage found in directory <{self.id}>."

        return
