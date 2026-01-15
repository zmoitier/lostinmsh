"""T-conform mesh a polygon."""

from dataclasses import dataclass
from pathlib import PurePath
from typing import Self

import gmsh
from numpy import concatenate, cos, linspace, pi, sin, vstack
from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist

from ..circular_iterable import circular_pairwise
from ..geometry import Corner, Geometry, Polygon
from ..type_alias import Tag, Vec2
from .context_manager import GmshContextManager, GmshOptions
from .mesh_boundary import mesh_exterior


@dataclass(frozen=True, slots=True)
class CornerTag:
    """Tags of a corner."""

    r: float
    p: int  # corner.angle = angles[corner.p]
    pt: list[Tag]
    lt: list[Tag]

    def get_edge_0(self: Self) -> tuple[tuple[Tag, Tag, Tag], tuple[Tag, Tag]]:
        return ((self.pt[1], self.pt[0], self.pt[-1]), (self.lt[0], self.lt[-1]))

    def get_edge_p(self: Self) -> tuple[tuple[Tag, Tag, Tag], tuple[Tag, Tag]]:
        return (
            (self.pt[self.p - 1], self.pt[self.p], self.pt[self.p + 1]),
            (self.lt[self.p - 1], self.lt[self.p]),
        )

    def get_lt_inn(self: Self) -> list[Tag]:
        return self.lt[1 : self.p - 1]

    def get_lt_out(self: Self) -> list[Tag]:
        return self.lt[self.p + 1 : -1]


def mesh_loc_struct(
    geometry: Geometry,
    mesh_size: float,
    gmsh_options: GmshOptions | None = None,
    *,
    corner_radius_shrink: float = 0.75,
    corner_geometric_coef: float = 1.5,
) -> PurePath | None:
    """T-conform mesh a polygon.

    Parameters
    ----------
    geometry : Geometry
    mesh_size : float
    gmsh_options: GmshOptions, optional
    corner_radius_shrink : float, default=0.75
    corner_geometric_coef : float, default=1.5
    """

    if not (0 < corner_radius_shrink < 1):
        raise ValueError("corner_radius_shrink must be in (0, 1).")

    if gmsh_options is None:
        gmsh_options = GmshOptions()

    with GmshContextManager(gmsh_options) as ctx:
        radius_max = _max_corner_radius(geometry) * corner_radius_shrink

        loop_tags: list[Tag] = []
        surface_tags_out: list[Tag] = []
        for polygon in geometry.polygons:
            loop_tag, st_inn, st_out, lt_bdy = _mesh_lost_polygon(
                polygon, radius_max, mesh_size, corner_geometric_coef
            )
            loop_tags.append(loop_tag)
            surface_tags_out.extend(st_out)

            ctx.update_domain_tags(
                {
                    (2, polygon.name): st_inn,
                    (1, f"{polygon.name}_boundary"): lt_bdy,
                }
            )

        ctx.update_domain_tags(
            {(2, geometry.boundary.background_name): surface_tags_out}
        )

        dom_tags = mesh_exterior(geometry.boundary, mesh_size, loop_tags)
        ctx.update_domain_tags(dom_tags)

    return gmsh_options.filename


def _max_corner_radius(geometry: Geometry) -> float:
    """Maximum corner radius."""

    points = vstack([polygon.vertices for polygon in geometry.polygons])

    ch = ConvexHull(points)
    ch_pts = points[ch.vertices]

    return min(
        pdist(points).min() / 2, geometry.boundary.dist_to_inner_boundary(ch_pts)
    )


def _mesh_lost_polygon(
    polygon: Polygon, radius_max: float, mesh_size: float, corner_coef: float
) -> tuple[Tag, list[Tag], list[Tag], list[Tag]]:
    """T-conform mesh of a polygon."""

    surface_tags_inn: list[Tag] = []
    surface_tags_out: list[Tag] = []
    line_tags_bdy: list[Tag] = []

    corner_tags: list[CornerTag] = []
    for vertex, corner in zip(polygon.vertices, polygon.corners):
        corner_tag, st_inn, st_out, lt_bdy = _mesh_lost_corner(
            vertex, corner, radius_max, mesh_size, corner_coef
        )
        corner_tags.append(corner_tag)
        surface_tags_inn.extend(st_inn)
        surface_tags_out.extend(st_out)
        line_tags_bdy.extend(lt_bdy)

    lt_inn: list[Tag] = []
    lt_out: list[Tag] = []
    for (ct0, ctp), length in zip(circular_pairwise(corner_tags), polygon.lengths):
        lt_inn.extend(ct0.get_lt_inn()[::-1])
        lt_out.extend(ct0.get_lt_out())

        lti, lto, sti, sto, ltb = _mesh_lost_edge(ct0, ctp, length, mesh_size)
        lt_inn.append(lti)
        lt_out.append(lto)
        surface_tags_inn.append(sti)
        surface_tags_out.append(sto)
        line_tags_bdy.append(ltb)

    surface_tags_inn.append(
        gmsh.model.geo.add_plane_surface([gmsh.model.geo.add_curve_loop(lt_inn)])
    )

    loop_tag_out: Tag = gmsh.model.geo.add_curve_loop(lt_out)
    return (loop_tag_out, surface_tags_inn, surface_tags_out, line_tags_bdy)


def _mesh_lost_corner(
    center: Vec2,
    corner: Corner,
    radius_max: float,
    mesh_size: float,
    corner_coef: float,
) -> tuple[CornerTag, list[Tag], list[Tag], list[Tag]]:
    """T-conform mesh of a corner."""

    c_tag: Tag = gmsh.model.geo.add_point(center[0], center[1], 0, mesh_size)

    # corner.angle = angles[corner.p]
    angles = concatenate(
        (
            linspace(0, corner.angle, num=corner.p + 1)[0:-1],
            linspace(corner.angle, 2 * pi, num=corner.q + 1)[0:-1],
        ),
    )
    points = center.reshape(2, 1) + radius_max * (
        corner.axis @ vstack((cos(angles), sin(angles)))
    )
    pt: list[Tag] = [
        gmsh.model.geo.add_point(points[0, j], points[1, j], 0, mesh_size)
        for j in range(points.shape[1])
    ]

    lt_rad: list[Tag] = [gmsh.model.geo.add_line(c_tag, t) for t in pt]
    lt_ang: list[Tag] = [
        gmsh.model.geo.add_line(a, b) for a, b in circular_pairwise(pt)
    ]

    n = max(2, round(1 + radius_max / mesh_size))
    for t in lt_rad:
        gmsh.model.geo.mesh.set_transfinite_curve(t, n, coef=corner_coef)
    for t in lt_ang:
        gmsh.model.geo.mesh.set_transfinite_curve(t, n)

    st: list[Tag] = [
        gmsh.model.geo.add_plane_surface([gmsh.model.geo.add_curve_loop([a, t, -b])])
        for (a, b), t in zip(circular_pairwise(lt_rad), lt_ang)
    ]
    for t in st:
        gmsh.model.geo.mesh.set_transfinite_surface(t)

    return (
        CornerTag(radius_max, corner.p, pt, lt_ang),
        st[: corner.p],
        st[corner.p :],
        [lt_rad[0], lt_rad[corner.p]],
    )


def _mesh_lost_edge(
    ct0: CornerTag, ctp: CornerTag, length: float, mesh_size: float
) -> tuple[Tag, Tag, Tag, Tag, Tag]:
    """T-conform mesh of a edge."""

    pt0, lt0 = ct0.get_edge_0()
    ptp, ltp = ctp.get_edge_p()

    lt_edge = [gmsh.model.geo.add_line(a, b) for a, b in zip(pt0, ptp)]

    n = max(2, round(1 + (length - ct0.r - ctp.r) / mesh_size))
    for t in lt_edge:
        gmsh.model.geo.mesh.set_transfinite_curve(t, n)

    st_inn = gmsh.model.geo.add_plane_surface(
        [gmsh.model.geo.add_curve_loop([-lt0[0], lt_edge[1], -ltp[0], -lt_edge[0]])]
    )
    gmsh.model.geo.mesh.set_transfinite_surface(st_inn, arrangement="Left")

    st_out = gmsh.model.geo.add_plane_surface(
        [gmsh.model.geo.add_curve_loop([lt0[1], lt_edge[1], ltp[1], -lt_edge[2]])]
    )
    gmsh.model.geo.mesh.set_transfinite_surface(st_out, arrangement="Right")

    return (-lt_edge[0], lt_edge[2], st_inn, st_out, lt_edge[1])
