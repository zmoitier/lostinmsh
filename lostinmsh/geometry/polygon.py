from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Self

from numpy import arctan2, asarray, greater, lexsort, pi
from numpy.linalg import norm
from numpy.typing import ArrayLike

from ..circular_iterable import circular_triplewise
from ..type_alias import Mat2x2, MatNx2, Vec2, VecN


@dataclass(slots=True)
class Corner:
    """Corner class."""

    angle: float
    axis: Mat2x2
    p: int
    q: int

    def __init__(
        self: Self, angle: float, axis: Mat2x2, max_denominator: int = 12
    ) -> None:
        self.angle = angle
        self.axis = axis

        r = Fraction(angle / pi).limit_denominator(max_denominator)
        s = Fraction(r.numerator, 2 * r.denominator - r.numerator)
        p, q = s.numerator, s.denominator
        if p == 1 or q == 1:
            p *= 2
            q *= 2

        self.p = p
        self.q = q

    # def critical_interval(self: Self) -> tuple[float, float]:
    #     """Return the critical interval of an angle.

    #     Returns
    #     -------
    #     tuple[Fraction, Fraction]
    #         The critical interval of the angle.
    #     """

    #     a = (2 - self) / self
    #     b = 1 / a

    #     if self > 1:
    #         return (-b, -a)

    #     return (-a, -b)


@dataclass(kw_only=True, slots=True)
class Polygon:
    """Polygon class."""

    name: str
    vertices: MatNx2
    corners: list[Corner]
    lengths: VecN = field(repr=False)

    @classmethod
    def from_vertices(
        cls, vertices: ArrayLike, name: str, *, max_denominator: int = 12
    ) -> Self:
        """Create a polygon from its vertices.

        Parameters
        ----------
        vertices : ArrayLike
            Array like of shape (N, 2) containing the polygon vertices.
        name : str
            Name of the polygon.
        max_denominator : int, optional, default 32
            Maximum denominator for angle approximation.
        Returns
        -------
        Polygon
        """

        pts = _ensure_counterclockwise(_validate_vertices(vertices))
        return cls(
            name=name,
            vertices=pts,
            corners=_compute_corners(pts, max_denominator),
            lengths=_compute_lengths(pts),
        )

    # def critical_interval(self: Self) -> tuple[Fraction, Fraction]:
    #     """Compute the largest critical interval of all angles.

    #     Returns
    #     -------
    #     tuple[Fraction, Fraction]
    #         Critical interval of the polygon.
    #     """

    #     a, b = self.corners[0].critical_interval()
    #     for corner in self.corners[1:]:
    #         interval = corner.critical_interval()
    #         a = min(a, interval[0])
    #         b = max(b, interval[1])

    #     return (a, b)

    def __str__(self: Self) -> str:
        lines: list[str] = [f'Polygon "{self.name}"']
        for i, (v, c) in enumerate(zip(self.vertices, self.corners)):
            lines.append(
                f"  Vertex {i}: ({v[0]:+.4f}, {v[1]:+.4f}), angle: {c.angle / pi:.4f} π"
            )
        return "\n".join(lines)


def _validate_vertices(vertices: ArrayLike) -> MatNx2:
    """Validate the shape of the vertices array."""

    pts = asarray(vertices, dtype=float)

    if len(pts.shape) != 2:
        raise ValueError("Vertices must be a two dimensional array.")

    nb_row, nb_col = pts.shape

    if not ((nb_row >= 3) and (nb_col == 2)):
        raise ValueError("vertices must have a shape (N, 2) with N ≥ 3.")

    return pts


def _ensure_counterclockwise(vertices: MatNx2) -> MatNx2:
    """Return the vertices in the counterclockwise direction."""

    # Find the vertex with the smallest x (and y to break ties)
    i: int = lexsort((vertices[:, 1], vertices[:, 0]))[0]

    n: int = vertices.shape[0]
    AB = vertices[(i + 1) % n, :] - vertices[i, :]
    AC = vertices[(i - 1) % n, :] - vertices[i, :]

    if AB[0] * AC[1] - AB[1] * AC[0] < 0:
        return vertices[::-1, :]

    return vertices


def _compute_lengths(vertices: MatNx2) -> VecN:
    """Compute side lengths."""

    idx = [*range(vertices.shape[0]), 0]
    lengths = norm(vertices[idx[1:], :] - vertices[idx[:-1], :], axis=1)

    if not all(greater(lengths, 1e-8)):
        raise ValueError("There is two vertices too close.")

    return lengths


def _compute_corners(vertices: MatNx2, max_denominator: int) -> list[Corner]:
    """Compute angles at the polygon's vertices."""
    n = vertices.shape[0]

    angles: list[Corner] = []
    for C, A, B in circular_triplewise(vertices, start=n - 1):
        u, v = _normalize(B - A), _normalize(C - A)

        _cos = u[0] * v[0] + u[1] * v[1]
        _sin = u[0] * v[1] - u[1] * v[0]
        angle: float = arctan2(_sin, _cos)
        if angle < 0:
            angle = 2 * pi + angle

        angles.append(
            Corner(
                angle,
                asarray([[u[0], -u[1]], [u[1], u[0]]]),
                max_denominator,
            )
        )

    return angles


def _normalize(vector: Vec2) -> Vec2:
    """Normalize vector."""

    return vector / norm(vector)
