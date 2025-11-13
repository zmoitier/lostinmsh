from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from math import gcd, lcm
from typing import Self

from numpy import arctan2, asarray, greater, lexsort, pi
from numpy.linalg import norm
from numpy.typing import ArrayLike

from ..circular_iterable import circular_triplewise
from ..type_alias import MatNx2, Vec2, VecN


class RationalAngle(Fraction):
    """Represent the angle `r * π` where `r` is a fraction."""

    def value(self: Self) -> float:
        """Return the angle value."""
        return self * pi

    def elementary_angle(self: Self) -> RationalAngle:
        """Compute the elementary angle.

        For an angle `aπ/b` we compute a rational `r` such that there exists integers
        `p, q, k` such that `p, q > 1`, `a/b = pr`, `2 - a/b = qr`, and `2 = kr`.

        Returns
        -------
        RationalAngle
        """

        a, b = self.numerator, self.denominator
        c = gcd(a, 2 * b - a)
        p, q = a // c, (2 * b - a) // c

        if p == 1 or q == 1:
            return RationalAngle(1, p + q)

        return RationalAngle(2, p + q)

    def critical_interval(self: Self) -> tuple[Fraction, Fraction]:
        """Return the critical interval of an angle.

        Returns
        -------
        tuple[Fraction, Fraction]
            The critical interval of the angle.
        """

        a = (2 - self) / self
        b = 1 / a

        if self > 1:
            return (-b, -a)

        return (-a, -b)

    def __str__(self) -> str:
        if self.numerator == 0:
            return "0"

        if self.numerator == 1:
            str_num = ""
        elif self.numerator == -1:
            str_num = "-"
        else:
            str_num = f"{self.numerator}"

        return f"{str_num}π/{self.denominator}"


@dataclass(kw_only=True, slots=True)
class Polygon:
    """Polygon class."""

    name: str
    vertices: MatNx2
    angles: list[RationalAngle]
    lengths: VecN = field(repr=False)

    @classmethod
    def from_vertices(
        cls, vertices: ArrayLike, name: str, *, max_denominator: int = 32
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
        lengths = _compute_lengths(pts)
        angles = _compute_angles(pts, max_denominator)

        return cls(name=name, vertices=pts, angles=angles, lengths=lengths)

    def elementary_angle(self: Self) -> RationalAngle:
        """Compute the common elementary angle.

        Returns
        -------
        RationalAngle
            Common elementary angle of the polygon.
        """

        angles = set(self.angles)

        return RationalAngle(
            gcd(*{a.numerator for a in angles}), lcm(*{a.denominator for a in angles})
        )

    def critical_interval(self: Self) -> tuple[Fraction, Fraction]:
        """Compute the largest critical interval of all angles.

        Returns
        -------
        tuple[Fraction, Fraction]
            Critical interval of the polygon.
        """

        a, b = self.angles[0].critical_interval()
        for corner in self.angles[1:]:
            interval = corner.critical_interval()
            a = min(a, interval[0])
            b = max(b, interval[1])

        return (a, b)

    def __str__(self: Self) -> str:
        lines: list[str] = [f'Polygon "{self.name}"']
        for i, (v, angle) in enumerate(zip(self.vertices, self.angles)):
            lines.append(
                f"  Vertex {i}: ({v[0]:+.4f}, {v[1]:+.4f}), angle: {str(angle)}"
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


def _compute_angles(vertices: MatNx2, max_denominator: int) -> list[RationalAngle]:
    """Compute angles at the polygon's vertices."""

    n: int = vertices.shape[0]

    angles: list[RationalAngle] = [
        _compute_angle(_normalize(B - A), _normalize(C - A), max_denominator)
        for C, A, B in circular_triplewise(vertices)
    ]

    if sum(angles) != n - 2:
        raise ValueError(
            "Error in the angle's computation at the polygon's vertices, the issue "
            "might comes from:\n"
            "  • The angles are badly approximate by a rational times π.\n"
            "    - Possible solution is to increase max_denominator="
            f"{max_denominator}.\n"
            "  • The polygon is not simple."
        )

    return angles


def _normalize(vector: Vec2) -> Vec2:
    """Normalize vector."""

    return vector / norm(vector)


def _compute_angle(u: Vec2, v: Vec2, max_denominator: int) -> RationalAngle:
    """Compute the angle between two vector."""

    _cos = u[0] * v[0] + u[1] * v[1]
    _sin = u[0] * v[1] - u[1] * v[0]
    angle = Fraction(arctan2(_sin, _cos) / pi).limit_denominator(max_denominator)

    if angle < 0:
        angle = 2 + angle

    return RationalAngle(angle)
