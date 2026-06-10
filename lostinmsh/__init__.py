"""GMSH toolbox for locally structured meshes on polygon."""

__version__ = "1.0.0"

__all__: list[str] = [
    "__version__",
    "geometry",
    "Polygon",
    "CircularBoundary",
    "circular_boundary",
    "RectangularBoundary",
    "rectangular_boundary",
    "Geometry",
    "mesh",
    "GmshOptions",
    "open_msh_file",
    "mesh_unstructured",
    "mesh_locally_structured",
    "plot",
    "plot_polygon",
    "plot_geometry",
    "plot_mesh",
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
