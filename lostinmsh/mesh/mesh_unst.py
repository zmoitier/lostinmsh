"""Mesh a polygon."""

from pathlib import PurePath
from typing import Final

import gmsh

from ..circular_iterable import circular_pairwise
from ..geometry import Geometry, Polygon
from ..type_alias import DimName, Tag
from .context_manager import GmshContextManager, GmshOptions
from .mesh_boundary import mesh_exterior

GEO: Final = gmsh.model.geo


def mesh_unstructured(
    geometry: Geometry, mesh_size: float, gmsh_options: GmshOptions = GmshOptions()
) -> PurePath | None:
    """Unstructured mesh of a geometry.

    Parameters
    ----------
    geometry : Geometry
    mesh_size : float
    gmsh_options : GmshOptions | None, optional, default None

    Returns
    -------
    PurePath | None
        Filename of the output mesh file or None if not saved.
    """
    with GmshContextManager(gmsh_options) as ctx:
        poly_loop_tags: list[Tag] = []

        for polygon in geometry.polygons:
            poly_loop_tag, dom_tags = mesh_unst_poly(polygon, mesh_size)
            poly_loop_tags.append(poly_loop_tag)

            ctx.update_domain_tags(dom_tags)

        dom_tags = mesh_exterior(geometry.boundary, mesh_size, poly_loop_tags)
        ctx.update_domain_tags(dom_tags)

    return gmsh_options.filename


def mesh_unst_poly(polygon: Polygon, h: float) -> tuple[Tag, dict[DimName, list[Tag]]]:
    """Mesh the polygon.

    Parameters
    ----------
    polygon : Polygon
        polygon object
    h : float
        target mesh size

    Returns
    -------
    tuple[Tag, dict[DimName, list[Tag]]]
        return the loop tag and the domain and its associated tags
    """
    point_tags: list[Tag] = [
        GEO.add_point(vertex[0], vertex[1], 0, h) for vertex in polygon.vertices
    ]

    line_tags = [GEO.add_line(a, b) for a, b in circular_pairwise(point_tags)]
    loop_tag = GEO.add_curve_loop(line_tags)
    surface_tag = GEO.add_plane_surface([loop_tag])

    return (
        loop_tag,
        {(2, polygon.name): [surface_tag], (1, f"{polygon.name}_boundary"): line_tags},
    )
