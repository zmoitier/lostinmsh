from typing import Any

from numpy import floating
from numpy.typing import NDArray

Float = floating[Any]

Vec2 = NDArray[Float]  # shape (2,)
Mat2x2 = NDArray[Float]  # shape (2, 2)

VecN = NDArray[Float]  # shape (N,) with N ≥ 1
MatNx2 = NDArray[Float]  # shape (N, 2) with N ≥ 1

Tag = int
DimName = tuple[int, str]
