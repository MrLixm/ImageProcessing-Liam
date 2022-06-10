"""

"""
from __future__ import annotations
import numbers
from abc import ABC
from typing import Optional, overload, Type, TypeVar, Tuple, Union

import numpy

__all__ = (
    "BaseVector",
    "V2f",
    "V3f",
)

TVector = TypeVar("TVector", bound="BaseVector")


class BaseVector(ABC, numpy.ndarray):

    # TODO doctsring needed

    _shape: Tuple[int] = NotImplemented
    _default: Tuple[float] = NotImplemented
    _axis: Tuple[str] = NotImplemented

    def __new__(cls, *args, **kwargs) -> TVector:

        if not args and not kwargs:
            return cls(*cls._default)

        elif args and kwargs:
            raise ValueError(
                f"Mix of kwargs and args is not supported : {args} ; {kwargs}"
            )

        elif args and not kwargs:

            if len(args) == 1:

                if isinstance(args[0], cls):
                    return args[0].copy()

                if isinstance(args[0], numpy.ndarray):
                    assert (
                        args[0].shape == cls._shape
                    ), f"Given array arg is not a {cls._shape[0]}x1 vector but {args[0].shape}"
                    return args[0].view(cls)

                if isinstance(args[0], list):
                    array = numpy.array(args[0])
                    assert (
                        array.shape == cls._shape
                    ), f"Given list arg {args[0]} is not a {cls._shape[0]}x1 vector."
                    return array.view(cls)

                if isinstance(args[0], numbers.Number):
                    return cls(numpy.full(cls._shape, args[0]))

            elif len(args) == cls._shape[0]:

                if all([isinstance(arg, numbers.Number) for arg in args]):
                    return cls(numpy.array(args))

        # kwargs just call back to above args
        elif not args and kwargs:

            axis_values = [v for k, v in kwargs.items() if k in cls._axis]
            if axis_values and all(
                [isinstance(axisv, numbers.Number) for axisv in axis_values]
            ):
                return cls(*axis_values)

            k = kwargs.get("array")
            if isinstance(k, (numpy.ndarray, cls, list)):
                return cls(k)

            if not kwargs.get("array", True) or not all(
                [kwargs.get(k, True) for k in kwargs.keys()]
            ):
                return cls()

        raise ValueError(
            f"The given arguments doesn't resolve to a new instance:\n"
            f"{args} ; {kwargs}"
        )

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]


class V2f(BaseVector):

    _shape = (2,)
    _default = (0.0, 0.0)
    _axis = ("x", "y")

    @overload
    def __init__(self, x: numbers.Number, y: numbers.Number):
        ...

    @overload
    def __init__(self, array: Optional[Union[numpy.ndarray, V2f]]):
        ...

    @overload
    def __init__(self, *args: Optional[Union[numpy.ndarray, V2f, numbers.Number]]):
        ...

    @overload
    def __init__(self):
        ...

    def __init__(self, *args, **kwargs):
        super().__init__()

    def to_v3f(self, third_axis: float = 0.0) -> V3f:
        return V3f(self.x, self.y, third_axis)


class V3f(BaseVector):

    _shape = (3,)
    _default = (0.0, 0.0, 0.0)
    _axis = ("x", "y", "z")

    @overload
    def __init__(self, x: numbers.Number, y: numbers.Number, z: numbers.Number):
        ...

    @overload
    def __init__(self, array: Optional[Union[numpy.ndarray, V3f]]):
        ...

    @overload
    def __init__(self, *args: Optional[Union[numpy.ndarray, V3f, numbers.Number]]):
        ...

    @overload
    def __init__(self):
        ...

    def __init__(self, *args, **kwargs):
        super().__init__()

    @property
    def z(self) -> float:
        return self[2]
