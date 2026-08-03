"""Geometry module."""

__all__: list[str] = [
    "CircularBoundary",
    "Corner",
    "ExteriorBoundary",
    "Geometry",
    "Polygon",
    "RectangularBoundary",
    "circular_boundary",
    "rectangular_boundary",
    "smallest_circle",
    "smallest_rectangle",
]

from .boundary import (
    CircularBoundary,
    ExteriorBoundary,
    RectangularBoundary,
    circular_boundary,
    rectangular_boundary,
)
from .geometry import Geometry
from .polygon import Corner, Polygon
from .smallest_boundary import smallest_circle, smallest_rectangle
