""" GMSH toolbox for T-coforme meshes on polygon. """

__version__ = "0.0.0"

__author__ = "Camille Carvalho, Zoïs Moitier"

__all__ = [
    "AutoCircular",
    "AutoRectangular",
    "Circular",
    "Geometry",
    "mesh",
    "mesh_Tconform",
    "Polygon",
    "plot_geometry",
    "plot_polygon",
    "Rectangular",
]


from .boundary import AutoCircular, AutoRectangular, Circular, Rectangular
from .geometry import Geometry
from .mesh import mesh
from .mesh_Tconform import mesh_Tconform
from .plot import plot_geometry, plot_polygon
from .polygon import Polygon
