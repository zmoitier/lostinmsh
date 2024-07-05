"""T-conform mesh a polygon."""


from dataclasses import dataclass
from pathlib import PurePath
from typing import Optional

import gmsh
from numpy import cos, linspace, pi, sin, sqrt

from ..circular_iterable import circular_pairwise
from ..geometry import Angle, Corner, Geometry, Polygon
from .gmsh_context_manager import GmshContextManager, GmshOptions
from .helper_type import Domain, DomainTags, SurfaceTags, update_domain_tags
from .mesh_border import _mesh_border


@dataclass(frozen=True, kw_only=True, slots=True)
class CornerTag:
    """Class for corner's tag."""

    pts_cav: list[int]
    pts_vac: list[int]
    lines_cav: list[int]
    lines_vac: list[int]


@dataclass(frozen=True, kw_only=True, slots=True)
class EgdeTag:
    """Class for edge's tag."""

    line_cav: int
    line_vac: int


def mesh_loc_struct(
    geometry: Geometry,
    mesh_size: float,
    gmsh_options: Optional[GmshOptions] = None,
    *,
    corner_radius_shrink: float = 0.75,
    corner_geometric_coef: float = 1.5,
) -> Optional[PurePath]:
    """T-confrom mesh a polygon.

    Parameters
    ----------
    geom : Geometry
    mesh_size : float
    gmsh_options: GmshOptions, optional
    corner_radius_shrink : float, default=0.75
    corner_geometric_coef : float, default=1.5
    """

    if gmsh_options is None:
        gmsh_options = GmshOptions()

    domain_tags: DomainTags = {}

    corner_radius = geometry.max_corner_radius() * corner_radius_shrink

    with GmshContextManager(gmsh_options) as gmsh_context_manager:
        loop_polygons = []
        surfaces_vac = []
        for polygon in geometry.polygons:
            l_poly, s_poly, s_vac = _tmesh_polygon(
                polygon, corner_radius, mesh_size, corner_geometric_coef
            )
            loop_polygons.append(l_poly)
            surfaces_vac.extend(s_vac)

            update_domain_tags(domain_tags, {Domain(polygon.name, 2): s_poly})

        loop_tag_inn, dom_tags = _mesh_border(geometry.border, mesh_size)
        domain_tags.update(dom_tags)

        domain_tags.update(
            {
                Domain(geometry.border.background_name, 2): [
                    gmsh.model.geo.addPlaneSurface([loop_tag_inn, *loop_polygons])
                ],
            }
        )

        gmsh_context_manager.domain_tags.update(domain_tags)

    return gmsh_options.filename


def _tmesh_polygon(
    polygon: Polygon, corner_radius: float, h: float, corner_coef: float
) -> tuple[int, SurfaceTags, SurfaceTags]:
    """T-coform mesh of a polygon."""

    ϕ = polygon.get_elementary_angle()
    r = min(corner_radius, h)  # / (2 * sin(ϕ.value / 2)))
    h_corner = sqrt(h * r * 2 * sin(ϕ.value / 2))

    corners_tag = []
    surfaces_cav = []
    surfaces_vac = []
    N_corner = max(2, round(1 + r / h))

    for corner in polygon.corners:
        c_tag, s_cav, s_vac = _mesh_corner(corner, r, ϕ, h, N_corner, corner_coef)
        corners_tag.append(c_tag)
        surfaces_cav.extend(s_cav)
        surfaces_vac.extend(s_vac)

    edges_tag = []
    for l, (C, D) in zip(polygon.lengths, circular_pairwise(corners_tag)):
        N_edge = max(2, round(1 + (l - 2 * r) / h_corner))
        e_tag, s_cav, s_vac = _mesh_edge(C, D, N_edge)
        edges_tag.append(e_tag)
        surfaces_cav.extend(s_cav)
        surfaces_vac.extend(s_vac)

    loop_inn, loop_out = _get_loops(corners_tag, edges_tag)

    surfaces_cav.append(gmsh.model.geo.addPlaneSurface([loop_inn]))

    print(surfaces_vac)

    return (loop_out, surfaces_cav, surfaces_vac)


def _mesh_corner(
    corner: Corner, r: float, ϕ: Angle, h: float, N: int, f: float
) -> tuple[CornerTag, list[int], list[int]]:
    """Mesh corner."""

    p, q = _compute_pq(corner.angle, ϕ)

    C = gmsh.model.geo.addPoint(corner.c[0], corner.c[1], 0, h)
    points = [
        gmsh.model.geo.addPoint(*to_global(corner, r, θ), 0, h)
        for θ in linspace(0, 2 * pi, num=p + q, endpoint=False)
    ]

    lines_rad = [gmsh.model.geo.addLine(C, A) for A in points]
    lines_ang = [gmsh.model.geo.addLine(A, B) for A, B in circular_pairwise(points)]

    for line in lines_rad:
        gmsh.model.geo.mesh.setTransfiniteCurve(line, N, coef=f)
    for line in lines_ang:
        gmsh.model.geo.mesh.setTransfiniteCurve(line, N)

    loops = []
    for i, j in circular_pairwise(range(p + q)):
        loops.append(
            gmsh.model.geo.addCurveLoop([lines_rad[i], lines_ang[i], -lines_rad[j]])
        )

    surfaces = []
    for loop in loops:
        s = gmsh.model.geo.addPlaneSurface([loop])
        gmsh.model.geo.mesh.setTransfiniteSurface(s)
        surfaces.append(s)

    return (
        CornerTag(
            pts_cav=points[:p],
            pts_vac=points[p:],
            lines_cav=lines_ang[:p],
            lines_vac=lines_ang[p:],
        ),
        surfaces[:p],
        surfaces[p:],
    )


def _compute_pq(angle: Angle, ϕ: Angle) -> tuple[int, int]:
    "Compute p and q such that a / b = 2p / (p+q) and p, q >= 2."
    return (int(angle / ϕ), int((2 - angle) / ϕ))


def to_global(corner: Corner, r: float, θ: float) -> tuple[float, float]:
    """Transform the local corner coordinate to global coordinate."""
    cosθ, sinθ = cos(θ), sin(θ)
    return (
        corner.c[0] + r * (cosθ * corner.v1[0] - sinθ * corner.v1[1]),
        corner.c[1] + r * (sinθ * corner.v1[0] + cosθ * corner.v1[1]),
    )


def _mesh_edge(
    C: CornerTag, D: CornerTag, N: int
) -> tuple[EgdeTag, SurfaceTags, SurfaceTags]:
    """Mesh edge."""
    interface = gmsh.model.geo.addLine(C.pts_cav[0], D.pts_vac[0])
    line_cav = gmsh.model.geo.addLine(D.pts_cav[-1], C.pts_cav[1])
    line_vac = gmsh.model.geo.addLine(C.pts_vac[-1], D.pts_vac[1])

    for line in (interface, line_cav, line_vac):
        gmsh.model.geo.mesh.setTransfiniteCurve(line, N)

    surface_cav = gmsh.model.geo.addPlaneSurface(
        [
            gmsh.model.geo.addCurveLoop(
                [interface, -D.lines_cav[-1], line_cav, -C.lines_cav[0]]
            )
        ]
    )
    gmsh.model.geo.mesh.setTransfiniteSurface(surface_cav)

    surface_vac = gmsh.model.geo.addPlaneSurface(
        [
            gmsh.model.geo.addCurveLoop(
                [-interface, -D.lines_vac[0], line_vac, -C.lines_vac[-1]]
            )
        ]
    )
    gmsh.model.geo.mesh.setTransfiniteSurface(surface_vac)

    return (EgdeTag(line_cav=line_cav, line_vac=line_vac), [surface_cav], [surface_vac])


def _get_loops(
    corners_tag: list[CornerTag], edges_tag: list[EgdeTag]
) -> tuple[int, int]:
    """Get loop inner and outer."""
    loop_inn = []
    loop_out = []
    for c, e in zip(corners_tag, edges_tag):
        loop_inn.extend(c.lines_cav[1:-1])
        loop_inn.append(e.line_cav)

        loop_out.extend(c.lines_vac[1:-1])
        loop_out.append(e.line_vac)

    return (
        gmsh.model.geo.addCurveLoop([-l for l in loop_inn]),
        gmsh.model.geo.addCurveLoop(loop_out),
    )
