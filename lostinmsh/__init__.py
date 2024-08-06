"""GMSH toolbox for locally structured meshes on polygon."""

__version__ = "0.0.3.dev"

__author__ = "Zoïs Moitier, Camille Carvalho"

__all__ = [
    "Polygon",
    "Geometry",
    "CircularBorder",
    "circular_border",
    "RectangularBorder",
    "rectangular_border",
    "GmshOptions",
    "mesh_unstructured",
    "mesh_loc_struct",
    "plot_geometry",
    "plot_polygon",
]

from .geometry import (
    CircularBorder,
    Geometry,
    Polygon,
    RectangularBorder,
    circular_border,
    rectangular_border,
)
from .mesh import GmshOptions, mesh_loc_struct, mesh_unstructured
from .plot import plot_geometry, plot_polygon
