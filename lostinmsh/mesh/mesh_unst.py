"""Mesh a polygon."""

from pathlib import PurePath

import gmsh

from ..circular_iterable import circular_pairwise
from ..geometry import Geometry, Polygon
from ..type_alias import DimName, Tag
from .context_manager import GmshContextManager, GmshOptions
from .mesh_boundary import mesh_exterior


def mesh_unstructured(
    geometry: Geometry, mesh_size: float, gmsh_options: GmshOptions | None = None
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

    if gmsh_options is None:
        gmsh_options = GmshOptions()

    with GmshContextManager(gmsh_options) as ctx:
        poly_loop_tags: list[Tag] = []

        for polygon in geometry.polygons:
            poly_loop_tag, dom_tags = mesh_unst_poly(polygon, mesh_size)
            poly_loop_tags.append(poly_loop_tag)

            ctx.domain_tags.update(dom_tags)

        dom_tags = mesh_exterior(geometry.boundary, mesh_size, poly_loop_tags)
        ctx.domain_tags.update(dom_tags)

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
    tuple[Domain, LoopTag, SurfaceTag]
        return the loop tag and the domain and its associated tags
    """

    node_tags = [
        gmsh.model.geo.add_point(vertex[0], vertex[1], 0, h)
        for vertex in polygon.vertices
    ]

    line_tags = [gmsh.model.geo.add_line(A, B) for A, B in circular_pairwise(node_tags)]
    loop_tag = gmsh.model.geo.add_curve_loop(line_tags)
    surface_tag = gmsh.model.geo.add_plane_surface([loop_tag])

    return (
        loop_tag,
        {(2, polygon.name): [surface_tag], (1, f"{polygon.name}_boundary"): line_tags},
    )
