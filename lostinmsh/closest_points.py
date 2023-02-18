""" Find the smallest distance of a set of points.

https://www.geeksforgeeks.org/closest-pair-of-points-using-divide-and-conquer-algorithm/
https://stackoverflow.com/questions/39681407/find-minimum-distance-between-points
https://sites.cs.ucsb.edu/~suri/cs235/ClosestPair.pdf
"""


from numpy import absolute, argsort, inf, less, where
from numpy.linalg import norm
from numpy.typing import NDArray


def min_dist_naive(points: NDArray) -> float:
    """Smallest distance of a set of points."""
    n = points.shape[0]

    min_d = inf
    for i in range(n):
        P = points[i, :]
        for j in range(i + 1, n):
            Q = points[j, :]
            if (d := norm(P - Q)) < min_d:
                min_d = float(d)
    return min_d


def min_dist(points: NDArray) -> float:
    """Smallest distance of a set of points."""
    idx_sort_x = argsort(points[:, 0])
    return _min_dist_rec(points[idx_sort_x, :])


def _min_dist_rec(points: NDArray) -> float:
    """Smallest distance square of a set of points."""
    n = points.shape[0]

    if n <= 3:
        return min_dist_naive(points)

    idx_mid = n // 2
    M = points[idx_mid, :]

    dl = _min_dist_rec(points[:idx_mid])
    dr = _min_dist_rec(points[idx_mid:])
    d = min(dl, dr)

    idx_strip = where(less(absolute(points[:, 0] - M[0]), d))[0]

    return min(d, _min_dist_strip(points[idx_strip, :], d))


def _min_dist_strip(points: NDArray, d: float) -> float:
    """Smallest distance strip."""
    n = points.shape[0]
    min_d = d

    idx_sort_y = argsort(points[:, 1])

    for i in range(n):
        P = points[idx_sort_y[i], :]
        for j in range(i + 1, n):
            Q = points[idx_sort_y[j], :]
            if Q[1] - P[1] >= min_d:
                break
            if (t := norm(P - Q)) < min_d:
                min_d = float(t)

    return min_d
