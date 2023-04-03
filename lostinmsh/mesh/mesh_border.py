"""Helper function for meshes function."""


import gmsh
from numpy.typing import NDArray

from ..circular_iterable import circular_pairwise
from ..geometry import Border, Circular, Rectangular
from .helper_type import CurveTags, Domain, LoopTag, Tags


def _mesh_border(
    border: Border, mesh_size: float
) -> tuple[LoopTag, dict[Domain, Tags]]:
    """Mesh the exterior.

    Parameters
    ----------
    border : Border
        the border
    mesh_size : float
        target mesh size

    Returns
    -------
    tuple[LoopTag, dict[Domain, Tags]]
        return the inner loop tag and the tags associated to the domains

    Raises
    ------
    ValueError
        Unknown border shape
    """

    if isinstance(border, Circular):
        return _mesh_circular(border, mesh_size)

    if isinstance(border, Rectangular):
        return _mesh_rectangular(border, mesh_size)

    raise ValueError("Unknown border shape.")


def _mesh_circular(
    circ: Circular, mesh_size: float
) -> tuple[LoopTag, dict[Domain, Tags]]:
    """Mesh circular mesh.

    Parameters
    ----------
    circ : Circular
        circular border
    mesh_size : float
        target mesh size

    Returns
    -------
    tuple[LoopTag, dict[Domain, Tags]]
        return the inner loop tag and the tags associated to the domains
    """

    loop_tag_inn, line_tags = _loop_circle(circ.center, circ.radius, mesh_size)
    domain_tags = {Domain(f"{circ.background_name}_boundary", 1): line_tags}

    if circ.thickness is not None:
        loop_tag_out, line_tags = _loop_circle(
            circ.center, circ.radius + circ.thickness, mesh_size
        )
        domain_tags.update(
            {
                Domain(circ.thickness_name, 2): [
                    gmsh.model.geo.addPlaneSurface([loop_tag_out, loop_tag_inn])
                ],
                Domain(f"{circ.thickness_name}_boundary", 1): line_tags,
            }
        )

    return (loop_tag_inn, domain_tags)


def _mesh_rectangular(
    rect: Rectangular, mesh_size: float
) -> tuple[LoopTag, dict[Domain, Tags]]:
    """Mesh circular mesh.

    Parameters
    ----------
    rect : Rectangular
        rectangular border
    mesh_size : float
        target mesh size

    Returns
    -------
    tuple[LoopTag, dict[Domain, Tags]]
        return the inner loop tag and the tags associated to the domains
    """

    loop_tag_inn, line_tags = _loop_rectangle(
        rect.center, rect.half_width, rect.half_height, mesh_size
    )
    domain_tags = {Domain(f"{rect.background_name}_boundary", 1): line_tags}

    if rect.thickness is not None:
        loop_tag_out, line_tags = _loop_rectangle(
            rect.center,
            rect.half_width + rect.thickness,
            rect.half_height + rect.thickness,
            mesh_size,
        )
        domain_tags.update(
            {
                Domain(rect.thickness_name, 2): [
                    gmsh.model.geo.addPlaneSurface([loop_tag_out, loop_tag_inn])
                ],
                Domain(f"{rect.thickness_name}_boundary", 1): line_tags,
            }
        )

    return (loop_tag_inn, domain_tags)


def _loop_circle(center: NDArray, radius: float, h: float) -> tuple[LoopTag, CurveTags]:
    """Return loop corresponding to a circle.

    Parameters
    ----------
    center : NDArray
        center of the circle
    radius : float
        radius of the circle
    h : float
        target mesh size

    Returns
    -------
    tuple[LoopTag, CurveTags]
        return inner loop tag and the list of lineTag
    """

    cx, cy = center

    C = gmsh.model.geo.addPoint(cx, cy, 0, h)
    node_tag = [
        gmsh.model.geo.addPoint(cx + x, cy + y, 0, h)
        for x, y in zip([radius, 0, -radius, 0], [0, radius, 0, -radius])
    ]

    line_tags = [
        gmsh.model.geo.addCircleArc(A, C, B) for A, B in circular_pairwise(node_tag)
    ]

    return (gmsh.model.geo.addCurveLoop(line_tags), line_tags)


def _loop_rectangle(
    center: NDArray, half_width: float, half_height: float, h: float
) -> tuple[LoopTag, CurveTags]:
    """Return loop corresponding to a circle.

    Parameters
    ----------
    center : NDArray
        center of the circle
    half_width : float
        half width of the rectangle
    half_height : float
        half height of the rectangle
    h : float
        target mesh size

    Returns
    -------
    tuple[LoopTag, CurveTags]
        return inner loop tag and the list of lineTag
    """

    cx, cy = center

    node_tag = [
        gmsh.model.geo.addPoint(cx + x, cy + y, 0, h)
        for x, y in zip(
            [half_width, -half_width, -half_width, half_width],
            [half_height, half_height, -half_height, -half_height],
        )
    ]

    line_tags = [gmsh.model.geo.addLine(A, B) for A, B in circular_pairwise(node_tag)]

    return (gmsh.model.geo.addCurveLoop(line_tags), line_tags)
