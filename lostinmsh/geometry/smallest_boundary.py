from math import sqrt

from numpy import amax, amin, array, float64
from numpy.random import default_rng
from scipy.spatial import ConvexHull

from ..type_alias import Float, MatNx2, Vec2

Circle = tuple[Vec2, Float]

EPS_MUL: Float = float64(1 + 1e-12)


def smallest_circle(points: MatNx2) -> Circle:
    """Compute the smallest enclosing circle of a collection of 2D points using
    the Welzl's algorithm, see https://doi.org/10.1007/978-3-540-77974-2 section 4.7.

    Parameters
    ----------
    points : MatNx2

    Returns
    -------
    Circle
    """
    # ConvexHull needs at least 3 points.
    if points.shape[0] <= 3:
        pts = points
    else:
        ch = ConvexHull(points)
        pts = ch.points[ch.vertices]
        default_rng(0).shuffle(pts)

    return welzl(pts)


def welzl(points: MatNx2) -> Circle:
    """Welzl's algorithm, using the iterative move-to-front formulation.

    `points` is expected to be in random order for the expected O(n)
    running time to hold.
    """
    n = points.shape[0]

    if n == 0:
        raise ValueError("welzl: no points given")

    if n == 1:
        return (points[0], float64(0))

    circle = _smallest_circle_2_points(points[0], points[1])
    for i in range(2, n):
        if _is_inside(circle, points[i]):
            continue

        circle = _circle_one_bdy(points[:i], points[i])

    return circle


def _circle_one_bdy(points: MatNx2, q: Vec2) -> Circle:
    """Smallest circle enclosing `points` with `q` on the boundary."""
    circle = _smallest_circle_2_points(points[0], q)

    for i in range(1, points.shape[0]):
        if _is_inside(circle, points[i]):
            continue

        circle = _circle_two_bdy(points[:i], points[i], q)

    return circle


def _circle_two_bdy(points: MatNx2, q1: Vec2, q2: Vec2) -> Circle:
    """Smallest circle enclosing `points` with `q1` and `q2` on the
    boundary."""
    circle = _smallest_circle_2_points(q1, q2)

    for p in points:
        if not _is_inside(circle, p):
            circle = _circumcircle_triangle(q1, q2, p)

    return circle


def _smallest_circle_2_points(a: Vec2, b: Vec2) -> Circle:
    """Smallest circle enclosing two points."""
    center = (a + b) / 2
    dx, dy = a[0] - b[0], a[1] - b[1]
    radius = float64(sqrt(dx * dx + dy * dy) / 2)
    return (center, radius)


def _is_inside(circle: Circle, a: Vec2) -> bool:
    """Check if the point A is inside the circle."""
    c, r = circle
    return (a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2 < r**2 * EPS_MUL


def _circumcircle_triangle(a: Vec2, b: Vec2, c: Vec2) -> Circle:
    """Compute the circumcircle of a three points, see
    https://en.wikipedia.org/wiki/Circumcircle#Cartesian_coordinates."""
    ax, ay = a[0], a[1]
    m00, m01 = b[0] - ax, b[1] - ay
    m10, m11 = c[0] - ax, c[1] - ay
    r0 = (b[0] * b[0] + b[1] * b[1]) - (ax * ax + ay * ay)
    r1 = (c[0] * c[0] + c[1] * c[1]) - (ax * ax + ay * ay)

    det = 2 * (m00 * m11 - m01 * m10)
    cx = (r0 * m11 - m01 * r1) / det
    cy = (m00 * r1 - m10 * r0) / det

    center = array([cx, cy])
    dx, dy = cx - ax, cy - ay
    radius = float64(sqrt(dx * dx + dy * dy))
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
