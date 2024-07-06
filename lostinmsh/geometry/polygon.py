"""Polygon class."""

from dataclasses import dataclass, field
from fractions import Fraction
from math import gcd, lcm
from typing import Self, TypeAlias

from numpy import arctan2, asarray, greater, lexsort, pi
from numpy.linalg import norm
from numpy.typing import ArrayLike, NDArray

from ..circular_iterable import circular_triplewise

Vec2: TypeAlias = NDArray
MatNx2: TypeAlias = NDArray


class Angle(Fraction):
    """Represent the angle `r * π` where `r` is a fraction."""

    @property
    def value(self) -> float:
        """Return the angle value."""
        return float(self) * pi

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


def critical_interval(angle: Angle) -> tuple[Fraction, Fraction]:
    """Return the critical interval of an angle.

    Parameters
    ----------
    angle : Angle

    Returns
    -------
    tuple[Fraction, Fraction]
        The critical interval of the angle.
    """

    a = (2 - angle) / angle
    b = 1 / a

    if angle > 1:
        return (-b, -a)

    return (-a, -b)


def elementary_angle(angle: Angle) -> Angle:
    """Compute the elementary angle.

    We compute p and q such that a / b = 2p / (p+q) and p, q >= 2
    and return the angle 2/(p+q).

    Parameters
    ----------
    angle : Angle

    Returns
    -------
    Angle
    """

    match angle:
        case 0:
            return Angle(0, 1)
        case 2:
            return Angle(2, 1)
        case _:
            r = angle / (2 - angle)
            p, q = r.numerator, r.denominator

    # if p == 1:
    #     return Angle(1, p + q)

    return Angle(2, p + q)


@dataclass(kw_only=True, slots=True)
class Corner:
    """Corner class."""

    center: Vec2
    angle: Angle
    e1: Vec2 = field(repr=False)
    e2: Vec2 = field(repr=False)

    def critical_interval(self) -> tuple[Fraction, Fraction]:
        """Get the critical interval."""
        return critical_interval(self.angle)

    def elementary_angle(self) -> Angle:
        """Get the elementary angle."""
        return elementary_angle(self.angle)


@dataclass(kw_only=True, slots=True)
class Polygon:
    """Polygon class."""

    corners: list[Corner]
    lengths: NDArray = field(repr=False)
    name: str

    @classmethod
    def from_vertices(
        cls, vertices: ArrayLike, name: str, *, max_denominator: int = 32
    ) -> Self:
        """Create a polygon from the vertices."""
        pts = _fix_orientation(_to_array(vertices))

        lengths = _compute_lengths(pts)
        corners = _compute_corners(pts, max_denominator)

        return cls(corners=corners, name=name, lengths=lengths)

    @property
    def nb_side(self) -> int:
        """Return the angle value."""
        return len(self.lengths)

    def translate(self, vector: Vec2) -> None:
        """Translate the vertices of the polygon."""
        for corner in self.corners:
            corner.center = corner.center + vector

    def get_vertices(self) -> MatNx2:
        """Get vertices."""
        return asarray([corner.center for corner in self.corners])

    def get_elementary_angle(self) -> Angle:
        """Get the elementary angle."""
        angles = {corner.elementary_angle() for corner in self.corners}
        return Angle(
            gcd(*{a.numerator for a in angles}), lcm(*{a.denominator for a in angles})
        )

    def critical_interval(self) -> tuple[Fraction, Fraction]:
        """Get the critical interval."""
        a, b = self.corners[0].critical_interval()
        for corner in self.corners[1:]:
            interval = corner.critical_interval()
            a = min(a, interval[0])
            b = max(b, interval[1])

        return (a, b)


def _to_array(vertices: ArrayLike) -> NDArray:
    """Check the shape of the vertices array."""
    pts = asarray(vertices)

    if len(pts.shape) != 2:
        raise ValueError("Vertices must be a two dimensional array.")

    nb_row, nb_col = pts.shape

    if not ((nb_row >= 3) and (nb_col == 2)):
        raise ValueError("vertices must have a shape (N, 2) with N ≥ 3.")

    return pts


def _fix_orientation(vertices: NDArray) -> NDArray:
    """Return the vertices in the counterclockwise direction."""
    n = vertices.shape[0]
    i = lexsort((vertices[:, 1], vertices[:, 0]))[0]

    C = vertices[(i - 1) % n, :]
    A = vertices[i, :]
    B = vertices[(i + 1) % n, :]
    AB = B - A
    AC = C - A

    if AB[0] * AC[1] - AB[1] * AC[0] < 0:
        return vertices[::-1, :]

    return vertices


def _compute_lengths(vertices: NDArray) -> NDArray:
    """Compute lengths."""
    index = [*range(vertices.shape[0]), 0]
    lengths = norm(vertices[index[1:], :] - vertices[index[:-1], :], axis=1)

    if not all(greater(lengths, 1e-8)):
        raise ValueError("There is two vertices too close.")

    return lengths


def _compute_corners(vertices: NDArray, max_denominator: int) -> list[Corner]:
    """Compute corners."""
    n = vertices.shape[0]

    corners = []
    for C, A, B in circular_triplewise(vertices, start=n - 1):
        AB = _normalize(B - A)
        AC = _normalize(C - A)
        angle = _compute_angle(AB, AC, max_denominator)
        corners.append(Corner(center=A, angle=angle, e1=AB, e2=AC))

    if sum(c.angle for c in corners) != n - 2:
        raise ValueError(
            "Error in the angle's computation at the polygon's corners, the issue "
            "might comes from:\n"
            "  • The angles are badly approximate by a rational times π.\n"
            "    - Possible solution is to increase max_denominator="
            f"{max_denominator}.\n"
            "  • The polygon is not simple."
        )

    return corners


def _normalize(vector: Vec2) -> Vec2:
    """Normalize vector."""
    return vector / norm(vector)


def _compute_angle(u: Vec2, v: Vec2, max_denominator: int) -> Angle:
    """Compute the angle between two vector."""
    _cos = u[0] * v[0] + u[1] * v[1]
    _sin = u[0] * v[1] - u[1] * v[0]
    angle = Fraction(arctan2(_sin, _cos) / pi).limit_denominator(max_denominator)

    if angle < 0:
        angle = 2 + angle

    return Angle(angle)
