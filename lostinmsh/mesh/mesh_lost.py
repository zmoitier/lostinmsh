"""T-conform mesh a polygon."""

from dataclasses import dataclass
from itertools import chain
from pathlib import PurePath
from typing import Final, Self

import gmsh
from numpy import concatenate, cos, linspace, pi, sin, sqrt, vstack
from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist

from ..circular_iterable import circular, circular_pairwise
from ..compatibility import batched
from ..geometry import Corner, Geometry, Polygon
from ..type_alias import Tag, Vec2
from .context_manager import GmshContextManager, GmshOptions
from .mesh_boundary import mesh_exterior

GEO: Final = gmsh.model.geo


@dataclass(frozen=True, slots=True)
class CornerTag:
    """Tags of a corner."""

    r: float  # corner radius
    h: float  # corner angular mesh size
    k: int  # corner.angle tag = pt[corner.k]
    pt: list[Tag]  # point tags
    lt: list[Tag]  # line tags

    def get_edge_0(self: Self) -> tuple[tuple[Tag, Tag, Tag], tuple[Tag, Tag]]:
        return ((self.pt[1], self.pt[0], self.pt[-1]), (self.lt[0], self.lt[-1]))

    def get_edge_p(self: Self) -> tuple[tuple[Tag, Tag, Tag], tuple[Tag, Tag]]:
        return (
            (self.pt[self.k - 1], self.pt[self.k], self.pt[self.k + 1]),
            (self.lt[self.k - 1], self.lt[self.k]),
        )

    def get_lt_inn(self: Self) -> list[Tag]:
        return self.lt[1 : self.k - 1]

    def get_lt_out(self: Self) -> list[Tag]:
        return self.lt[self.k + 1 : -1]


def mesh_locally_structured(
    geometry: Geometry, mesh_size: float, gmsh_options: GmshOptions = GmshOptions()
) -> PurePath | None:
    """T-conform mesh a polygon.

    Parameters
    ----------
    geometry : Geometry
    mesh_size : float
    gmsh_options: GmshOptions, optional
    """
    with GmshContextManager(gmsh_options) as ctx:
        corner_radius = min(1.5 * mesh_size, _max_corner_radius(geometry) * 0.5)

        loop_tags: list[Tag] = []
        surface_tags_out: list[Tag] = []
        for polygon in geometry.polygons:
            loop_tag, st_inn, st_out, poly_lt_bdy = _mesh_lost_polygon(
                polygon, corner_radius, mesh_size
            )
            loop_tags.append(loop_tag)
            surface_tags_out.extend(st_out)

            ctx.update_domain_tags(
                {
                    (2, polygon.name): st_inn,
                    (1, f"{polygon.name}_boundary"): poly_lt_bdy,
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
    polygon: Polygon, corner_radius: float, mesh_size: float
) -> tuple[Tag, list[Tag], list[Tag], list[Tag]]:
    """T-conform mesh of a polygon."""
    surface_tags_inn: list[Tag] = []
    surface_tags_out: list[Tag] = []
    poly_line_tags: list[Tag] = []

    corner_tags: list[CornerTag] = []
    for vertex, corner in zip(polygon.vertices, polygon.corners):
        corner_tag, st_inn, st_out, poly_lts_bdy = _mesh_lost_corner(
            vertex, corner, corner_radius
        )
        corner_tags.append(corner_tag)
        surface_tags_inn.extend(st_inn)
        surface_tags_out.extend(st_out)
        poly_line_tags.extend(poly_lts_bdy)

    lt_inn: list[Tag] = []
    lt_out: list[Tag] = []
    for (ct0, ctp), length in zip(circular_pairwise(corner_tags), polygon.lengths):
        lt_inn.extend(ct0.get_lt_inn()[::-1])
        lt_out.extend(ct0.get_lt_out())

        lti, lto, sti, sto, poly_lt_bdy = _mesh_lost_edge(ct0, ctp, length, mesh_size)
        lt_inn.append(lti)
        lt_out.append(lto)
        surface_tags_inn.append(sti)
        surface_tags_out.append(sto)
        poly_line_tags.append(poly_lt_bdy)

    surface_tags_inn.append(GEO.add_plane_surface([GEO.add_curve_loop(lt_inn)]))

    loop_tag_out: Tag = GEO.add_curve_loop(lt_out)
    return (loop_tag_out, surface_tags_inn, surface_tags_out, poly_line_tags)


def _mesh_lost_corner(
    center: Vec2, corner: Corner, radius: float
) -> tuple[CornerTag, list[Tag], list[Tag], list[Tag]]:
    """T-conform mesh of a corner."""
    xp = 2 * sin(corner.angle / (4 * corner.p))
    xq = 2 * sin((2 * pi - corner.angle) / (4 * corner.q))
    h_corner = radius * sqrt(xp * xq)

    c_tag: Tag = GEO.add_point(center[0], center[1], 0)

    # corner.angle = angles_inn[corner.p] = angles_out[2*corner.p]
    angles0 = concatenate(
        (
            linspace(0, corner.angle, num=corner.p + 1)[0:-1],
            linspace(corner.angle, 2 * pi, num=corner.q + 1)[0:-1],
        ),
    )
    angles1 = concatenate(
        (
            linspace(0, corner.angle, num=2 * corner.p + 1)[0:-1],
            linspace(corner.angle, 2 * pi, num=2 * corner.q + 1)[0:-1],
        ),
    )

    points0 = center.reshape(2, 1) + (radius / 3) * (
        corner.axis @ vstack((cos(angles0), sin(angles0)))
    )
    points1 = center.reshape(2, 1) + radius * (
        corner.axis @ vstack((cos(angles1), sin(angles1)))
    )

    pt0: list[Tag] = [
        GEO.add_point(points0[0, j], points0[1, j], 0, h_corner)
        for j in range(points0.shape[1])
    ]
    pt1: list[Tag] = [
        GEO.add_point(points1[0, j], points1[1, j], 0, h_corner)
        for j in range(points1.shape[1])
    ]

    lt_rad: list[list[Tag]] = [
        [GEO.add_line(c_tag, t) for t in pt0],
        [GEO.add_line(a, b) for a, b in zip(pt0, pt1[::2])],
        [GEO.add_line(a, b) for a, b in zip(pt0, pt1[1::2])],
        [GEO.add_line(a, b) for a, b in zip(circular(pt0, start=1), pt1[1::2])],
    ]
    lt_ang: list[list[Tag]] = [
        [GEO.add_line(a, b) for a, b in circular_pairwise(pt0)],
        [GEO.add_line(a, b) for a, b in circular_pairwise(pt1)],
    ]

    for t in chain(chain.from_iterable(lt_rad), chain.from_iterable(lt_ang)):
        GEO.mesh.set_transfinite_curve(t, 2)

    st_inn: list[Tag] = []
    st_out: list[Tag] = []
    for i, ((lr00, lr01), (lr10, lr11), lr2, lr3, la0, (la1, la2)) in enumerate(
        zip(
            circular_pairwise(lt_rad[0]),
            circular_pairwise(lt_rad[1]),
            lt_rad[2],
            lt_rad[3],
            lt_ang[0],
            batched(lt_ang[1], 2),
        )
    ):
        st: list[Tag] = [
            GEO.add_plane_surface([GEO.add_curve_loop([lr00, la0, -lr01])]),
            GEO.add_plane_surface([GEO.add_curve_loop([lr10, la1, -lr2])]),
            GEO.add_plane_surface([GEO.add_curve_loop([lr2, -lr3, -la0])]),
            GEO.add_plane_surface([GEO.add_curve_loop([lr3, la2, -lr11])]),
        ]
        if i < corner.p:
            st_inn.extend(st)
        else:
            st_out.extend(st)

    for t in chain(st_inn, st_out):
        GEO.mesh.set_transfinite_surface(t)

    return (
        CornerTag(radius, h_corner, 2 * corner.p, pt1, lt_ang[1]),
        st_inn,
        st_out,
        [lt_rad[0][0], lt_rad[1][0], lt_rad[0][corner.p], lt_rad[1][corner.p]],
    )


def _mesh_lost_edge(
    ct0: CornerTag, ctp: CornerTag, length: float, mesh_size: float
) -> tuple[Tag, Tag, Tag, Tag, Tag]:
    """T-conform mesh of a edge."""
    pt0, lt0 = ct0.get_edge_0()
    ptp, ltp = ctp.get_edge_p()

    lt_edge = [GEO.add_line(a, b) for a, b in zip(pt0, ptp)]

    h = sqrt(mesh_size * sqrt(ct0.h * ctp.h))
    n = max(2, round(1 + (length - ct0.r - ctp.r) / h))
    for t in lt_edge:
        GEO.mesh.set_transfinite_curve(t, n)

    st_inn = GEO.add_plane_surface(
        [GEO.add_curve_loop([-lt0[0], lt_edge[1], -ltp[0], -lt_edge[0]])]
    )
    GEO.mesh.set_transfinite_surface(st_inn, arrangement="Left")

    st_out = GEO.add_plane_surface(
        [GEO.add_curve_loop([lt0[1], lt_edge[1], ltp[1], -lt_edge[2]])]
    )
    GEO.mesh.set_transfinite_surface(st_out, arrangement="Right")

    return (-lt_edge[0], lt_edge[2], st_inn, st_out, lt_edge[1])
