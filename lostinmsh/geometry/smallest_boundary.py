from numpy import amax, amin, array, float64, inf, sum
from numpy.linalg import norm
from numpy.random import shuffle
from scipy.spatial import ConvexHull

from ..circular_iterable import circular_triplewise
from .helper_type import Float, MatNx2, Vec2

type Circle = tuple[Vec2, Float]

EPS_ADD: Float = float64(1e-12)
EPS_MUL: Float = float64(1) + EPS_ADD


def smallest_circle(points: MatNx2) -> Circle:
    """Compute the smallest enclosing circle of a collection of 2D points using
    the Welzl's algorithm, see https://doi.org/10.1007/BFb0038202.

    Parameters
    ----------
    points : MatNx2

    Returns
    -------
    Circle
    """

    if points.shape[0] <= 3:
        return trivial_circle(list(points))

    ch = ConvexHull(points)
    pts = ch.points[ch.vertices]
    shuffle(pts)

    return welzl(pts, [], pts.shape[0])


def welzl(points: MatNx2, boundary: list[Vec2], length: int) -> Circle:
    """Welzl algorithm."""

    if length == 0 or len(boundary) == 3:
        return trivial_circle(boundary)

    P = points[length - 1]

    center, radius = welzl(points, boundary.copy(), length - 1)
    if _is_inside((center, radius), P):
        return (center, radius)

    boundary.append(P)
    return welzl(points, boundary.copy(), length - 1)


def trivial_circle(pts: list[Vec2]) -> Circle:
    """Trivial circle."""

    match len(pts):
        case 0:
            return (array([inf, inf], dtype=float64), float64(0))

        case 1:
            return (pts[0], float64(0))

        case 2:
            return _smallest_circle_2_points(pts[0], pts[1])

        case 3:
            return _smallest_circle_3_points(pts[0], pts[1], pts[2])

        case _:
            raise ValueError("Must have 0 ≤ len(pts) ≤ 3.")


def _smallest_circle_2_points(a: Vec2, b: Vec2) -> Circle:
    """Compute the smallest enclosing circle of two points."""

    center = (a + b) / 2
    radius = norm(a - b) / 2
    return (center, radius)


def _smallest_circle_3_points(a: Vec2, b: Vec2, c: Vec2) -> Circle:
    """Compute the smallest enclosing circle of three points."""

    for p, q, r in circular_triplewise((a, b, c)):
        circle = _smallest_circle_2_points(p, q)
        if _is_inside(circle, r):
            return circle

    return _circumcircle_triangle(a, b, c)


def _is_inside(circle: Circle, a: Vec2) -> bool:
    """Check if the point A is inside the circle."""

    c, r = circle
    return (a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2 < r**2 * EPS_MUL


def _circumcircle_triangle(a: Vec2, b: Vec2, c: Vec2) -> Circle:
    """Compute the circumcircle of a three points, see
    https://en.wikipedia.org/wiki/Circumcircle#Circumcenter_vector."""

    ab_n2 = sum((b - a) ** 2)
    ac_n2 = sum((c - a) ** 2)
    bc_n2 = sum((c - b) ** 2)

    a_c = bc_n2 * (ac_n2 + ab_n2 - bc_n2)
    b_c = ac_n2 * (bc_n2 + ab_n2 - ac_n2)
    c_c = ab_n2 * (bc_n2 + ac_n2 - ab_n2)

    center = (a_c * a + b_c * b + c_c * c) / (a_c + b_c + c_c)
    radius = norm(center - a)
    return (center, radius)


def smallest_rectangle(points: MatNx2) -> tuple[Vec2, Vec2]:
    """Compute the smallest axes aligned rectangle of a collection of 2D
    points.

    Parameters
    ----------
    points : MatNx2

    Returns
    -------
    tuple[Vec2, Vec2]
        lower left and upper right corners of the rectangle
    """

    return (amin(points, axis=0), amax(points, axis=0))
