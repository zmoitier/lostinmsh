"""GMSH toolbox for locally structured meshes on polygon."""

__version__ = "0.1.0"

__author__ = "Zoïs Moitier, Camille Carvalho"

__all__: list[str] = [
    "geometry",
    "Polygon",
    "CircularBoundary",
    "circular_boundary",
    "RectangularBoundary",
    "rectangular_boundary",
    # "Geometry",
    # "GmshOptions",
    # "mesh_unstructured",
    # "mesh_loc_struct",
    # "plot_geometry",
    # "plot_polygon",
]

from . import geometry
from .geometry import (
    Polygon,
    CircularBoundary,
    RectangularBoundary,
    circular_boundary,
    rectangular_boundary,
)
