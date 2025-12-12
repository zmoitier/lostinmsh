"""Geometry module."""

__all__: list[str] = [
    "Corner",
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
from .polygon import Corner, Polygon
from .smallest_boundary import smallest_circle, smallest_rectangle
