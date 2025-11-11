from typing import Any

from numpy import floating
from numpy.typing import NDArray

type Float = floating[Any]

type Vec2 = NDArray[Float]  # shape (2,)
type VecN = NDArray[Float]  # shape (N,) with N ≥ 1
type MatNx2 = NDArray[Float]  # shape (N, 2) with N ≥ 1
