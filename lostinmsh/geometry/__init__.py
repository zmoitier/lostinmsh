"""Geometry module."""

__all__: list[str] = [
    "RationalAngle",
    "Polygon",
    "smallest_circle",
    "smallest_rectangle",
    "ExteriorBoundary",
    "CircularBoundary",
    "circular_boundary",
    "RectangularBoundary",
    "rectangular_boundary",
    "Geometry",
]

from .boundary import (
    CircularBoundary,
    ExteriorBoundary,
    RectangularBoundary,
    circular_boundary,
    rectangular_boundary,
)
from .geometry import Geometry
from .polygon import Polygon, RationalAngle
from .smallest_boundary import smallest_circle, smallest_rectangle
