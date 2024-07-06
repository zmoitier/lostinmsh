"""Class for boundary."""

from dataclasses import dataclass

from numpy import asarray
from numpy.linalg import norm
from numpy.typing import NDArray

from .smallest_boundary import smallest_circle, smallest_rectangle


@dataclass(kw_only=True, slots=True)
class Border:
    """Border class.

    Attributes
    ----------
    center : NDArray
        Center of the border.
    background_name : str
        Name of the background.
    thickness : float, optional
        Thickness of the border.
    thickness_name : str
        Name of the thickness.
    """

    center: tuple[float, float]
    background_name: str = "background"
    thickness: float | None = None
    thickness_name: str = "PML"

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        """Sign distance to the inner boundary.

        It is positive if all the points are inside and it is negative
        if at least one point is outside.

        Parameters
        ----------
        points : NDArray
            list of points should be an array of shape (N, 2) with N ≥ 1.
        """
        raise NotImplementedError()


@dataclass(kw_only=True, slots=True)
class Circular(Border):
    """Circular boundary."""

    radius: float

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        return self.radius - norm(points - asarray(self.center), axis=1).max()


@dataclass(kw_only=True, slots=True)
class Rectangular(Border):
    """Rectangular boundary."""

    half_width: float
    half_height: float

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        pts = points - self.center
        return min(
            self.half_width - pts[:, 0].max(), self.half_height - pts[:, 1].max()
        )


def circular(
    points: NDArray, border_factor: float, thickness_factor: float | None = None
) -> Circular:
    """Compute the circular boundary."""
    center, radius = smallest_circle(points)

    r0 = radius * (1 + border_factor)
    if thickness_factor is not None:
        thickness = radius * thickness_factor
    else:
        thickness = None

    return Circular(center=(center[0], center[1]), radius=r0, thickness=thickness)


def rectangular(
    points: NDArray,
    border_factor: float,
    thickness_factor: float | None = None,
) -> Rectangular:
    """Compute the rectangular boundary."""
    center, lengths = smallest_rectangle(points)

    r = float(norm(lengths))
    l0 = lengths + r * border_factor
    if thickness_factor is not None:
        thickness = r * thickness_factor
    else:
        thickness = None

    return Rectangular(
        center=(center[0], center[1]),
        half_width=l0[0],
        half_height=l0[1],
        thickness=thickness,
    )
