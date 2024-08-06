"""Geometry module."""

__all__ = [
    "RationalAngle",
    "critical_interval",
    "elementary_angle",
    "Corner",
    "Polygon",
    "Geometry",
    "Border",
    "CircularBorder",
    "RectangularBorder",
    "circular_border",
    "rectangular_border",
    "smallest_rectangle",
]

from .border import (
    Border,
    CircularBorder,
    RectangularBorder,
    circular_border,
    rectangular_border,
)
from .geometry import Geometry
from .polygon import Corner, Polygon, RationalAngle, critical_interval, elementary_angle
from .smallest_boundary import smallest_rectangle
