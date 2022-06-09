"""

"""
from __future__ import annotations
import numbers
from abc import ABC, abstractmethod
from typing import Optional, overload, Type, Union, List, Tuple, TypeVar

import numpy

from .vector import V3f, V2f, BaseVector

__all__ = (
    "BaseMatrix",
    "M33f",
    "M44f",
)

TMatrix = TypeVar("TMatrix", bound="BaseMatrix")


class BaseMatrix(ABC, numpy.ndarray):
    """
    Abstract class for all matrix components.
    """

    _shape: Tuple[float, float] = NotImplemented
    """
    Absolute shape of the ndarray
    """

    _identity: numpy.ndarray = NotImplemented
    """
    Ndarray considered as an identity matrix for the current shape.
    """

    @overload
    def __new__(
        cls,
        array: Optional[Union[TMatrix, numpy.ndarray, List[List[float, float, float]]]],
    ) -> TMatrix:
        ...

    @overload
    def __new__(cls, *args) -> TMatrix:
        ...

    def __new__(cls, *args, **kwargs) -> TMatrix:

        if not args and not kwargs:
            return cls(cls._identity.copy())

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
                    ), f"Given array arg is not a {cls._shape[0]}x{cls._shape[1]} matrix but {args[0].shape}"
                    return args[0].view(cls)

                if isinstance(args[0], list):
                    array = numpy.array(args[0])
                    assert (
                        array.shape == cls._shape
                    ), f"Given list arg {args[0]} is not a {cls._shape[0]}x{cls._shape[1]} matrix."
                    return array.view(cls)

            elif len(args) == cls._shape[0] * cls._shape[1]:

                if all([isinstance(arg, numbers.Number) for arg in args]):
                    return cls(numpy.array(args).reshape(cls._shape[0], cls._shape[1]))

        # kwargs just call back to above args
        elif not args and kwargs:

            k = kwargs.get("array")
            if isinstance(k, numpy.ndarray):
                return cls(k)

            elif isinstance(k, cls):
                return cls(k)

            elif isinstance(k, list):
                return cls(k)

            if not kwargs.get("array", True):
                return cls()

        raise ValueError(
            f"The given arguments doesn't resolve to a new instance:\n"
            f"{args} ; {kwargs}"
        )

    @abstractmethod
    def rotate(self, angle: numbers.Number):
        pass

    @abstractmethod
    def scale(self, v: BaseVector):
        pass

    @abstractmethod
    def translate(self, v: BaseVector):
        pass

    @abstractmethod
    def shear(self, v: BaseVector):
        pass

    def asNdarray(self) -> numpy.ndarray:
        """
        Return a view of the data but as a ``numpy.ndarray`` instance.

        .. note:: Modifying the view's data will also modify this instance's data.
        """
        return self.view(numpy.ndarray)

    def isIdentity(self) -> bool:
        """
        Returns:
            True if the current instance is an identity matrix.
        """
        return numpy.array_equal(self, self._identity)

    def makeIdentity(self):
        self[:] = self._identity.copy()

    def __mul__(self, other: Union[TMatrix, numbers.Number]):
        return numpy.dot(self, other)

    def __rmul__(self, other: Union[TMatrix, numbers.Number]):
        return numpy.dot(other, self).view(self.__class__)


class M33f(BaseMatrix):
    """
    3x3 matrix.
    This is it's identity::
        1.0 | 0.0 | 0.0
        0.0 | 1.0 | 0.0
        0.0 | 0.0 | 1.0

    Combinaison of args possible are :

    -
        number of args corresponding to the matrix shape like::

            M33f(1,0,0,0,1,0,0,0,1) where (3x3=9args)

    - 1 args out of :

        -
            existing instance::

                M33f(M33f())

        -
            Ndarray of a similar shape.
            No copy is made so change on the orignal array are applied
            on this instance and vice versa::

                M33f(numpy.ndarray(...))

        -
            3x3 list::

                M33f([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    - 0 args : ``M33f()`` which returns an identity matrix.

    """

    _shape = (3, 3)
    _identity = numpy.identity(3)

    def rotate(self, angle: numbers.Number):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L3117

        Args:
            angle: angle in radian
        """
        self[:] *= M33f().setRotation(angle)

    def setRotation(self, angle: numbers.Number):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L3092

        Args:
            angle: angle in radian
        """
        a_cos = numpy.cos(angle)
        a_sin = numpy.sin(angle)

        self[0][0] = a_cos
        self[0][1] = a_sin
        self[0][2] = 0
        self[1][0] = -a_sin
        self[1][1] = a_cos
        self[1][2] = 0
        self[2][0] = 0
        self[2][1] = 0
        self[2][2] = 1

    def scale(self, v: V2f):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L3172

        Args:
            v:
        """
        self[0] *= v.x
        self[0] *= v.y

    def translate(self, v: V2f):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L3216

        Args:
            v:
        """
        self[2] += v.x * self[0] + v.y * self[1]

    def shear(self, v: V2f):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L3286

        Args:
            v:
        """
        self[0] = self[0] + v.y * self[1]
        self[1] = self[1] + v.x * self[0]

    def to_m44f(self) -> M44f:
        return M44f(
            [
                [*self[0], 0],
                [*self[1], 0],
                [*self[2], 0],
                [0, 0, 0, 1],
            ]
        )


class M44f(BaseMatrix):
    """
    4x4 matrix.
    This is it's identity::
        1.0 | 0.0 | 0.0 | 0.0
        0.0 | 1.0 | 0.0 | 0.0
        0.0 | 0.0 | 1.0 | 0.0
        0.0 | 0.0 | 0.0 | 1.0

    Combinaison of args possible are :

    -
        number of args corresponding to the matrix shape like::

            M44f(1,0,0,0,0,1,0,0,0,...) where (4x4=16args)

    - 1 args out of :

        -
            existing instance::

                M44f(M44f())

        -
            Ndarray of a similar shape.
            No copy is made so change on the orignal array are applied
            on this instance and vice versa::

                M44f(numpy.ndarray(...))

        -
            3x3 list::

                M44f([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    - 0 args : ``M44f()`` which returns an identity matrix.

    """

    _shape = (4, 4)
    _identity = numpy.identity(4)

    def rotate(self, angle: V3f):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L4668

        Args:
            angle: vector of XYZ radian angles
        """

        cos_a = numpy.cos(angle)
        sin_a = numpy.sin(angle)

        m00 = cos_a.z * cos_a.y
        m01 = sin_a.z * cos_a.y
        m02 = -sin_a.y
        m10 = -sin_a.z * cos_a.x + cos_a.z * sin_a.y * sin_a.x
        m11 = cos_a.z * cos_a.x + sin_a.z * sin_a.y * sin_a.x
        m12 = cos_a.y * sin_a.x
        m20 = -sin_a.z * -sin_a.x + cos_a.z * sin_a.y * cos_a.x
        m21 = cos_a.z * -sin_a.x + sin_a.z * sin_a.y * cos_a.x
        m22 = cos_a.y * cos_a.x

        self[0] = self[0] * m00 + self[1] * m01 + self[2] * m02
        self[1] = self[0] * m10 + self[1] * m11 + self[2] * m12
        self[2] = self[0] * m20 + self[1] * m21 + self[2] * m22

    def scale(self, v: V3f):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L4779

        Args:
            v:
        """
        self[0] *= v.x
        self[1] *= v.y
        self[2] *= v.z

    def translate(self, v: V3f):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L4837

        Args:
            v:
        """
        self[3] += v.x * self[0] + v.y * self[1] + v.z * self[2]

    def shear(self, v: V3f):
        """
        SRC: https://github.dev/AcademySoftwareFoundation/Imath/blob/main/src/Imath/ImathMatrix.h#L4906

        Args:
            v:
        """
        for i in range(self._shape[-1]):
            self[2][i] += v.y * self[0][i] + v.z * self[1][i]
            self[1][i] += v.x * self[0][i]
