"""Geometry module."""

__all__ = [
    "Angle",
    "critical_interval",
    "elementary_angle",
    "Corner",
    "Polygon",
    "Geometry",
    "Border",
    "Circular",
    "Rectangular",
    "circular",
    "rectangular",
    "smallest_rectangle",
]

from .border import Border, Circular, Rectangular, circular, rectangular
from .geometry import Geometry
from .polygon import Angle, Corner, Polygon, critical_interval, elementary_angle
from .smallest_boundary import smallest_rectangle
