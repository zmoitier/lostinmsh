"""Mesh a polygon."""


from pathlib import PurePath
from typing import Optional

import gmsh

from .circular_iterable import circular_pairwise
from .geometry import Geometry
from .gmsh_context_manager import GmshContextManager, OptionalPathLike
from .mesh_border import _mesh_border
from .polygon import Polygon


def mesh(
    geom: Geometry,
    mesh_size: float,
    *,
    element_order: int = 1,
    terminal: bool = False,
    gui: bool = False,
    filename: OptionalPathLike = None,
    msh_file_version: Optional[float] = None,
    save_width: Optional[int] = None,
    save_height: Optional[int] = None,
    save_compress: bool = False,
    hide_model_Entities: bool = True,
) -> OptionalPathLike:
    """Mesh a geometry."""

    with GmshContextManager(
        element_order=element_order,
        terminal=terminal,
        gui=gui,
        filename=PurePath(filename) if filename is not None else None,
        msh_file_version=msh_file_version,
        save_width=save_width,
        save_height=save_height,
        save_compress=save_compress,
        hide_model_Entities=hide_model_Entities,
    ):
        loop_polygons = [_mesh_polygon(polygon, mesh_size) for polygon in geom.polygons]
        loop_border = _mesh_border(geom.border, mesh_size)

        s_vac = gmsh.model.geo.addPlaneSurface([loop_border, *loop_polygons])
        gmsh.model.addPhysicalGroup(dim=2, tags=[s_vac], name="Vacuum")

    return filename


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
