"""

"""
from __future__ import annotations

import numbers
from abc import ABC
from typing import Optional, overload, Type

import numpy

__all__ = ("BaseMatrix",)


class BaseMatrix(ABC, numpy.ndarray):
    pass
