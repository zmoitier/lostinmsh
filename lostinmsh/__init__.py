"""GMSH toolbox for locally structured meshes on polygon."""

__version__ = "0.0.3.dev"

__author__ = "Zoïs Moitier, Camille Carvalho"

__all__ = [
    "Polygon",
    "Geometry",
    "Circular",
    "Rectangular",
    "GmshOptions",
    "mesh_unstructured",
    "mesh_loc_struct",
    "plot_geometry",
    "plot_polygon",
]

from .geometry import Circular, Geometry, Polygon, Rectangular
from .mesh import GmshOptions, mesh_loc_struct, mesh_unstructured
from .plot import plot_geometry, plot_polygon
