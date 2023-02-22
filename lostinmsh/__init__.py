"""GMSH toolbox for T-coforme meshes on polygon."""

__version__ = "0.0.1"

__author__ = "Camille Carvalho, Zoïs Moitier"

__all__ = [
    "AutoCircular",
    "AutoRectangular",
    "Circular",
    "Geometry",
    "mesh",
    "mesh_lost",
    "Polygon",
    "plot_geometry",
    "plot_polygon",
    "Rectangular",
]


from .border import AutoCircular, AutoRectangular, Circular, Rectangular
from .geometry import Geometry
from .mesh import mesh
from .mesh_lost import mesh_loc_struct
from .plot import plot_geometry, plot_polygon
from .polygon import Polygon
