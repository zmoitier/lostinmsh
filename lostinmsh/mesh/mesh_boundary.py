from typing import Final

import gmsh

from ..circular_iterable import circular_pairwise
from ..geometry import CircularBoundary, ExteriorBoundary, RectangularBoundary
from ..type_alias import DimName, Tag, Vec2

GEO: Final = gmsh.model.geo


def mesh_exterior(
    boundary: ExteriorBoundary, mesh_size: float, inner_loop_tags: list[Tag]
) -> dict[DimName, list[Tag]]:
    """Mesh the exterior.

    Parameters
    ----------
    boundary : ExteriorBoundary
    mesh_size : float
    inner_loop_tags : list[Tag]

    Returns
    -------
    dict[DimName, list[Tag]]

    Raises
    ------
    ValueError
    """
    if isinstance(boundary, CircularBoundary):
        return _mesh_circular(boundary, mesh_size, inner_loop_tags)

    if isinstance(boundary, RectangularBoundary):
        return _mesh_rectangular(boundary, mesh_size, inner_loop_tags)

    raise ValueError("Unknown boundary shape.")


def _mesh_circular(
    circ: CircularBoundary, mesh_size: float, inner_loop_tags: list[Tag]
) -> dict[DimName, list[Tag]]:
    """Mesh circular mesh."""
    ct = GEO.add_point(circ.center[0], circ.center[1], 0, mesh_size)

    line_tags = _loop_circle(ct, circ.center, circ.radius, mesh_size)
    loop_tag_inn = GEO.add_curve_loop(line_tags)

    domain_tags = {
        (2, circ.background_name): [
            GEO.add_plane_surface([loop_tag_inn, *inner_loop_tags])
        ],
        (1, f"{circ.background_name}_boundary"): line_tags,
    }

    if circ.thickness is not None:
        line_tags = _loop_circle(
            ct, circ.center, circ.radius + circ.thickness, mesh_size
        )

        domain_tags.update(
            {
                (2, circ.thickness_name): [
                    GEO.add_plane_surface([GEO.add_curve_loop(line_tags), loop_tag_inn])
                ],
                (1, f"{circ.thickness_name}_boundary"): line_tags,
            }
        )

    return domain_tags


def _loop_circle(
    center_tag: Tag, center: Vec2, radius: float, mesh_size: float
) -> list[Tag]:
    """Return loop corresponding to a circle."""
    cx, cy = center
    point_tags = [
        GEO.add_point(cx + x, cy + y, 0, mesh_size)
        for x, y in ((radius, 0), (0, radius), (-radius, 0), (0, -radius))
    ]

    line_tags = [
        GEO.add_circle_arc(a, center_tag, b) for a, b in circular_pairwise(point_tags)
    ]

    return line_tags


def _mesh_rectangular(
    rect: RectangularBoundary, mesh_size: float, inner_loop_tags: list[Tag]
) -> dict[DimName, list[Tag]]:
    """Mesh rectangular mesh."""
    line_tags = _loop_rectangle(rect.corner_low, rect.corner_high, mesh_size)
    loop_tag_inn = GEO.add_curve_loop(line_tags)

    domain_tags = {
        (2, rect.background_name): [
            GEO.add_plane_surface([loop_tag_inn, *inner_loop_tags])
        ],
        (1, f"{rect.background_name}_boundary"): line_tags,
    }

    if rect.thickness is not None:
        line_tags = _loop_rectangle(
            rect.corner_low - rect.thickness,
            rect.corner_high + rect.thickness,
            mesh_size,
        )
        loop_tag_out = GEO.add_curve_loop(line_tags)
        domain_tags.update(
            {
                (2, rect.thickness_name): [
                    GEO.add_plane_surface([loop_tag_out, loop_tag_inn])
                ],
                (1, f"{rect.thickness_name}_boundary"): line_tags,
            }
        )

    return domain_tags


def _loop_rectangle(corner_low: Vec2, corner_high: Vec2, mesh_size: float) -> list[Tag]:
    """Return loop corresponding to a rectangle."""
    point_tags = [
        GEO.add_point(x, y, 0, mesh_size)
        for x, y in (
            (corner_low[0], corner_low[1]),
            (corner_high[0], corner_low[1]),
            (corner_high[0], corner_high[1]),
            (corner_low[0], corner_high[1]),
        )
    ]

    line_tags = [GEO.add_line(a, b) for a, b in circular_pairwise(point_tags)]

    return line_tags
