"""Geometry module."""

__all__ = [
    "Geometry",
    "Polygon",
    "Border",
    "Circular",
    "Rectangular",
    "AutoCircular",
    "AutoRectangular",
    "smallest_rectangle",
    "Angle",
    "Corner",
]

from .border import AutoCircular, AutoRectangular, Border, Circular, Rectangular
from .geometry import Geometry
from .polygon import Angle, Corner, Polygon
from .smallest_boundary import smallest_rectangle
