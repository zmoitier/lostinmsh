"""Comptute the smallest enclosing circle or rectangle."""


from numpy import arange, asarray, lexsort, ones, sort, sqrt, stack
from numpy.linalg import det, norm
from numpy.random import shuffle
from numpy.typing import NDArray

from ..circular_iterable import circular_triplewise

Circle = tuple[NDArray, float]

EPS_ADD: float = 1e-12
EPS_MUL: float = 1 + EPS_ADD


def convex_hull(points: NDArray) -> NDArray:
    """Computes the convex hull of a set of distinct 2D points.

    Implements Andrew's monotone chain algorithm from:
    A. M. Andrew, Another efficient algorithm for convex hulls in two dimensions
    https://doi.org/10.1016/0020-0190(79)90072-3
    and is heavly inspire by:
    https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain

    Parameters
    ----------
    points : NDArray of shape (N, 2)
        set of 2D points

    Returns
    -------
    convex_hull : NDArray
        the points defining the convex hull
    """
    if (n := points.shape[0]) <= 1:
        return arange(n)

    idx_sort = lexsort((points[:, 1], points[:, 0]))

    lower = _lower_hull(points, idx_sort)
    upper = _lower_hull(points, idx_sort[::-1])

    return points[sort([*lower[:-1], *upper[:-1]]), :]


def _lower_hull(pts: NDArray, idx_sort: NDArray) -> list[int]:
    """Lower hull."""
    lower: list[int] = []
    for i in idx_sort:
        while (
            len(lower) >= 2
            and _cross_product(pts[lower[-2], :], pts[lower[-1], :], pts[i, :])
            <= EPS_ADD
        ):
            lower.pop()

        lower.append(i)

    return lower


def _cross_product(o: NDArray, u: NDArray, v: NDArray) -> float:
    """Cross product."""
    return (u[0] - o[0]) * (v[1] - o[1]) - (u[1] - o[1]) * (v[0] - o[0])


def smallest_circle(points: NDArray) -> Circle:
    """Compute the smallest enclosing circle of a collection of vertices using
    the Welzl's algorithm, see https://doi.org/10.1007/BFb0038202."""

    if points.shape[0] == 3:
        return _smallest_circle_3_points(*points)

    pts = convex_hull(points)
    shuffle(pts)

    return welzl(list(pts), [], pts.shape[0])


def welzl(points: list[NDArray], boundary: list[NDArray], lenght: int) -> Circle:
    """Welzl algorithm."""

    if lenght == 0 or len(boundary) == 3:
        return trivial_circle(boundary)

    P = points[lenght - 1]

    center, radius = welzl(points, boundary.copy(), lenght - 1)
    if _is_inside((center, radius), P):
        return (center, radius)

    boundary.append(P)
    return welzl(points, boundary.copy(), lenght - 1)


def trivial_circle(R: list[NDArray]) -> Circle:
    """Trivial circle."""
    match len(R):
        case 0:
            return (asarray([0, 0]), 0)

        case 1:
            return (R[0], 0)

        case 2:
            return _smallest_circle_2_points(R[0], R[1])

        case 3:
            return _smallest_circle_3_points(R[0], R[1], R[2])

        case _:
            raise ValueError("The length of R must be ≤ 3.")


def _smallest_circle_2_points(A: NDArray, B: NDArray) -> Circle:
    """Compute the smallest enclosing circle of two points."""

    center = asarray([(A[0] + B[0]) / 2, (A[1] + B[1]) / 2])
    radius = sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2) / 2
    return (center, radius)


def _smallest_circle_3_points(A: NDArray, B: NDArray, C: NDArray) -> Circle:
    """Compute the smallest enclosing circle of three points."""

    for P, Q, R in circular_triplewise((A, B, C)):
        center, radius = _smallest_circle_2_points(P, Q)
        if _is_inside((center, radius), R):
            return (center, radius)

    return _circumcircle_triangle(A, B, C)


def _is_inside(circle: Circle, A: NDArray) -> bool:
    """Check if the point A is inside the circle."""
    C, r = circle
    return (A[0] - C[0]) ** 2 + (A[1] - C[1]) ** 2 < r**2 * EPS_MUL


def _circumcircle_triangle(A: NDArray, B: NDArray, C: NDArray) -> Circle:
    """Compute the circumcircle of a three points, see
    https://en.wikipedia.org/wiki/Circumscribed_circle."""
    points = asarray([A, B, C])

    norm2 = norm(points, axis=1) ** 2

    a = _det_col(points[:, 0], points[:, 1], ones(3))
    b = _det_col(points[:, 0], points[:, 1], norm2)

    cx = _det_col(norm2, points[:, 1], ones(3)) / (2 * a)
    cy = _det_col(points[:, 0], norm2, ones(3)) / (2 * a)

    return (asarray([cx, cy]), sqrt(b / a + cx * cx + cy * cy))


def _det_col(A: NDArray, B: NDArray, C: NDArray) -> float:
    """Compute the det of the matrix define by the colunm [A, B, C]."""
    return det(stack((A, B, C), axis=1))


def smallest_rectangle(points: NDArray) -> tuple[NDArray, NDArray]:
    """Find the smallest rectangle align with the coordinate axis."""
    xmin, xmax = points[:, 0].min(), points[:, 0].max()
    ymin, ymax = points[:, 1].min(), points[:, 1].max()

    center = asarray(((xmin + xmax) / 2, (ymin + ymax) / 2))
    lengths = asarray((xmax, ymax)) - center

    return (center, lengths)
