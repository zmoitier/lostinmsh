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
    "Geometry",
    "plot_polygon",
    "plot_geometry",
    "mesh",
    "GmshOptions",
    "open_msh_file",
    "mesh_unstructured",
    "mesh_loc_struct",
]

from . import geometry, mesh
from .geometry import (
    CircularBoundary,
    Geometry,
    Polygon,
    RectangularBoundary,
    circular_boundary,
    rectangular_boundary,
)
from .mesh import GmshOptions, mesh_loc_struct, mesh_unstructured, open_msh_file
from .plot import plot_geometry, plot_polygon  # type: ignore
