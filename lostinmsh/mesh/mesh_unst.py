"""Mesh a polygon."""


from pathlib import PurePath
from typing import Optional

import gmsh

from ..circular_iterable import circular_pairwise
from ..geometry import Geometry, Polygon
from .gmsh_context_manager import GmshContextManager, GmshOptions
from .helper_type import Domain, DomainTags, LoopTag, LoopTags, Tags, update_domain_tags
from .mesh_border import _mesh_border


def mesh_unstructured(
    geometry: Geometry, mesh_size: float, gmsh_options: Optional[GmshOptions] = None
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

    domain_tags: DomainTags = {}

    with GmshContextManager(gmsh_options) as gmsh_context_manager:
        loop_tags: LoopTags = []

        for polygon in geometry.polygons:
            loop_tag, dom_tags = _mesh_polygon(polygon, mesh_size)
            loop_tags.append(loop_tag)

            update_domain_tags(domain_tags, dom_tags)

        loop_tag_inn, dom_tags = _mesh_border(geometry.border, mesh_size)
        domain_tags.update(dom_tags)

        domain_tags.update(
            {
                Domain(geometry.border.background_name, 2): [
                    gmsh.model.geo.addPlaneSurface([loop_tag_inn, *loop_tags])
                ],
            }
        )

        gmsh_context_manager.domain_tags.update(domain_tags)

    return gmsh_options.filename


def _mesh_polygon(polygon: Polygon, h: float) -> tuple[LoopTag, dict[Domain, Tags]]:
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
        gmsh.model.geo.addPoint(corner.c[0], corner.c[1], 0, h)
        for corner in polygon.corners
    ]

    line_tags = [gmsh.model.geo.addLine(A, B) for A, B in circular_pairwise(node_tags)]

    loop_tag = gmsh.model.geo.addCurveLoop(line_tags)

    surface_tag = gmsh.model.geo.addPlaneSurface([loop_tag])

    return (
        loop_tag,
        {
            Domain(polygon.name, 2): [surface_tag],
            Domain(f"{polygon.name}_boundary", 1): line_tags,
        },
    )
