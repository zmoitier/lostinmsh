"""GMSH toolbox for locally structured meshes on polygon."""

__version__ = "0.0.2"

__author__ = "Zoïs Moitier, Camille Carvalho"

__all__ = [
    "Polygon",
    "Geometry",
    "Circular",
    "Rectangular",
    "AutoCircular",
    "AutoRectangular",
    "GmshOptions",
    "mesh",
    "mesh_loc_struct",
    "plot_geometry",
    "plot_polygon",
]

from .border import AutoCircular, AutoRectangular, Circular, Rectangular
from .geometry import Geometry
from .gmsh_context_manager import GmshOptions
from .mesh import mesh
from .mesh_lost import mesh_loc_struct
from .plot import plot_geometry, plot_polygon
from .polygon import Polygon
