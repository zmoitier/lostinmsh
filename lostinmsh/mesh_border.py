""" Helper function for meshes function. """


import gmsh
from numpy.typing import NDArray

from .border import Border, Circular, Rectangular
from .circular_iterable import circular_pairwise


def _mesh_border(border: Border, mesh_size: float) -> int:
    """Mesh the exterior."""

    if isinstance(border, Circular):
        return _mesh_circular(border, mesh_size)

    if isinstance(border, Rectangular):
        return _mesh_rectangular(border, mesh_size)

    raise ValueError("Unknown border shape.")


def _mesh_circular(circ: Circular, mesh_size: float) -> int:
    """Mesh circular border."""
    loop_inn = _loop_circle(circ.center, circ.radius, mesh_size, "Sigma")

    if circ.thickness is not None:
        loop_out = _loop_circle(
            circ.center, circ.radius + circ.thickness, mesh_size, "Sigma"
        )
        s_pml = gmsh.model.geo.addPlaneSurface([loop_out, loop_inn])
        gmsh.model.addPhysicalGroup(dim=2, tags=[s_pml], name="PML")

    return loop_inn


def _mesh_rectangular(rect: Rectangular, mesh_size: float) -> int:
    """Mesh rectangular border."""
    loop_inn = _loop_rectangle(
        rect.center, rect.half_width, rect.half_height, mesh_size, "Sigma"
    )

    if rect.thickness is not None:
        loop_out = _loop_rectangle(
            rect.center,
            rect.half_width + rect.thickness,
            rect.half_height + rect.thickness,
            mesh_size,
            "Sigma",
        )
        s_pml = gmsh.model.geo.addPlaneSurface([loop_out, loop_inn])
        gmsh.model.addPhysicalGroup(dim=2, tags=[s_pml], name="PML")

    return loop_inn


def _loop_circle(center: NDArray, radius: float, h: float, name: str) -> int:
    """Return loop corresponding to a circle."""
    cx, cy = center

    C = gmsh.model.geo.addPoint(cx, cy, 0, h)
    pts = [
        gmsh.model.geo.addPoint(cx + x, cy + y, 0, h)
        for x, y in zip([radius, 0, -radius, 0], [0, radius, 0, -radius])
    ]

    lines = [gmsh.model.geo.addCircleArc(A, C, B) for A, B in circular_pairwise(pts)]
    gmsh.model.addPhysicalGroup(dim=1, tags=lines, name=name)

    return gmsh.model.geo.addCurveLoop(lines)


def _loop_rectangle(
    center: NDArray, half_width: float, half_height: float, h: float, name: str
) -> int:
    """Return loop corresponding to a square."""
    cx, cy = center

    pts = [
        gmsh.model.geo.addPoint(cx + x, cy + y, 0, h)
        for x, y in zip(
            [half_width, -half_width, -half_width, half_width],
            [half_height, half_height, -half_height, -half_height],
        )
    ]

    lines = [gmsh.model.geo.addLine(A, B) for A, B in circular_pairwise(pts)]
    gmsh.model.addPhysicalGroup(dim=1, tags=lines, name=name)

    return gmsh.model.geo.addCurveLoop(lines)
