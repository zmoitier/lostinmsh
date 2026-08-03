"""GMSH toolbox for locally structured meshes on polygon."""

__version__ = "1.0.1"
__author__ = "Zoïs Moitier and Camille Carvalho"

__all__: list[str] = [
    "CircularBoundary",
    "Geometry",
    "GmshOptions",
    "Polygon",
    "RectangularBoundary",
    "__author__",
    "__version__",
    "circular_boundary",
    "geometry",
    "mesh",
    "mesh_locally_structured",
    "mesh_unstructured",
    "open_msh_file",
    "plot",
    "plot_geometry",
    "plot_mesh",
    "plot_polygon",
    "rectangular_boundary",
]

from . import geometry, mesh, plot
from .geometry import (
    CircularBoundary,
    Geometry,
    Polygon,
    RectangularBoundary,
    circular_boundary,
    rectangular_boundary,
)
from .mesh import GmshOptions, mesh_locally_structured, mesh_unstructured, open_msh_file
from .plot import plot_geometry, plot_mesh, plot_polygon  # type: ignore
