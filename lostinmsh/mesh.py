"""Mesh a polygon."""


from pathlib import PurePath
from typing import Optional

import gmsh

from .circular_iterable import circular_pairwise
from .geometry import Geometry
from .gmsh_context_manager import GmshContextManager, GmshOptions
from .mesh_border import _mesh_border
from .polygon import Polygon


def mesh(
    geom: Geometry, mesh_size: float, gmsh_options: Optional[GmshOptions] = None
) -> Optional[PurePath]:
    """Mesh a geometry.

    Parameters
    ----------
    geom : Geometry
    mesh_size : float
    gmsh_options: GmshOptions, optional
    """

    if gmsh_options is None:
        gmsh_options = GmshOptions()

    with GmshContextManager(gmsh_options):
        loop_polygons = [_mesh_polygon(polygon, mesh_size) for polygon in geom.polygons]
        loop_border = _mesh_border(geom.border, mesh_size)

        s_vac = gmsh.model.geo.addPlaneSurface([loop_border, *loop_polygons])
        gmsh.model.addPhysicalGroup(dim=2, tags=[s_vac], name="Vacuum")

    return gmsh_options.filename


def _mesh_polygon(polygon: Polygon, h: float) -> int:
    """Mesh polygon."""
    points = [
        gmsh.model.geo.addPoint(corner.c[0], corner.c[1], 0, h)
        for corner in polygon.corners
    ]

    lines = [gmsh.model.geo.addLine(A, B) for A, B in circular_pairwise(points)]

    loop = gmsh.model.geo.addCurveLoop(lines)

    surface = gmsh.model.geo.addPlaneSurface([loop])
    gmsh.model.addPhysicalGroup(dim=2, tags=[surface], name=polygon.name)

    return loop
