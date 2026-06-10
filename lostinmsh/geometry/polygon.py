from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

from numpy import abs, arange, arctan2, asarray, greater, inf, lexsort, log, pi
from numpy.linalg import norm
from numpy.typing import ArrayLike

from ..circular_iterable import circular_triplewise
from ..type_alias import Mat2x2, MatNx2, Vec2, VecN


@dataclass(frozen=True, slots=True)
class Corner:
    """Corner class."""

    angle: float
    axis: Mat2x2
    p: int
    q: int

    def critical_interval(self: Self) -> tuple[float, float]:
        """Return the critical interval of an angle.

        Returns
        -------
        tuple[float, float]
            The critical interval of the angle.
        """
        a = float((2 * pi - self.angle) / self.angle)
        b = 1 / a

        if a < 1:
            return (-b, -a)

        return (-a, -b)

    def discrete_critical_interval(self: Self) -> tuple[float, float]:
        """Return the discrete critical interval of an angle.

        Returns
        -------
        tuple[float, float]
            The discrete critical interval of the angle.
        """
        a, b = self.critical_interval()
        r = float((2 * pi - self.angle) * self.p / (self.angle * self.q))

        if r < 1:
            return (a / r, b * r)

        return (a * r, b / r)


@dataclass(kw_only=True, slots=True)
class Polygon:
    """Polygon class."""

    name: str
    vertices: MatNx2
    corners: list[Corner]
    lengths: VecN = field(repr=False)

    @classmethod
    def from_vertices(
        cls, vertices: ArrayLike, name: str, *, max_subdiv: int = 16
    ) -> Self:
        """Create a polygon from its vertices.

        Parameters
        ----------
        vertices : ArrayLike
            Array like of shape (N, 2) containing the polygon vertices.
        name : str
            Name of the polygon.
        max_subdiv : int, optional, default 16
            Maximum subdivision of the corner.
        Returns
        -------
        Polygon
        """
        pts = _ensure_counterclockwise(_validate_vertices(vertices))
        return cls(
            name=name,
            vertices=pts,
            corners=_compute_corners(pts, max_subdiv),
            lengths=_compute_lengths(pts),
        )

    def critical_interval(self: Self) -> tuple[float, float]:
        """Compute the critical interval of the polygon.

        Returns
        -------
        tuple[float, float]
            Critical interval of the polygon.
        """
        a, b = (inf, -inf)
        for corner in self.corners:
            interval = corner.critical_interval()
            a = min(a, interval[0])
            b = max(b, interval[1])

        return (a, b)

    def discrete_critical_interval(self: Self) -> tuple[float, float]:
        """Compute the discrete critical interval of the polygon.

        Returns
        -------
        tuple[float, float]
            Discrete critical interval of the polygon.
        """
        a, b = (inf, -inf)
        for corner in self.corners:
            interval = corner.discrete_critical_interval()
            a = min(a, interval[0])
            b = max(b, interval[1])

        return (a, b)

    def __str__(self: Self) -> str:
        lines: list[str] = [f'Polygon "{self.name}"']
        for i, (v, c) in enumerate(zip(self.vertices, self.corners)):
            lines.append(
                ", ".join(
                    [
                        f"  Vertex {i}: ({v[0]:+.4f}, {v[1]:+.4f})",
                        f"angle: {c.angle / pi:.4f} π",
                        f"(p, q): ({c.p}, {c.q})",
                    ]
                )
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


def _compute_corners(vertices: MatNx2, max_subdiv: int) -> list[Corner]:
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

        p, q = _compute_pq(angle, max_subdiv)
        angles.append(Corner(angle, asarray([[u[0], -u[1]], [u[1], u[0]]]), p, q))

    return angles


def _normalize(vector: Vec2) -> Vec2:
    """Normalize vector."""
    return vector / norm(vector)


def _compute_pq(angle: float, max_subdiv: int) -> tuple[int, int]:
    """Compute p and q for a given angle."""
    r = (2 * pi - angle) / angle

    p_min, q_min = 0, 0
    _min = abs(log(r))
    for n in range(4, max_subdiv + 1):
        p, q = arange(1, n - 1), arange(n - 1, 1, -1)
        v = abs(log(r * p / q))

        i = v.argmin()
        if v[i] < _min:
            p_min, q_min = p[i], q[i]
            _min = v[i]

        if _min < 1e-12:
            break

    return (p_min, q_min)
