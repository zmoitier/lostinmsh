from dataclasses import dataclass

from numpy import amax, amin, vstack
from numpy.linalg import norm

from .helper_type import MatNx2, Vec2
from .polygon import Polygon
from .smallest_boundary import smallest_circle, smallest_rectangle


@dataclass(kw_only=True, slots=True)
class Border:
    """Border class.

    Attributes
    ----------
    background_name : str
        Name of the background.
    thickness : float, optional
        Thickness of the border.
    thickness_name : str
        Name of the thickness.
    """

    background_name: str = "background"
    thickness: float | None = None
    thickness_name: str = "PML"

    def dist_to_inner_boundary(self, points: MatNx2) -> float:
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
class CircularBorder(Border):
    """Circular boundary."""

    center: Vec2
    radius: float

    def dist_to_inner_boundary(self, points: MatNx2) -> float:
        return self.radius - norm(points - self.center, axis=1).max()


def circular_border(
    polygons: list[Polygon], inner_factor: float, thickness_factor: float | None = None
) -> CircularBorder:
    """Compute the circular boundary."""

    center, radius = smallest_circle(_get_vertices(polygons))

    r0 = radius * (1 + inner_factor)
    if thickness_factor is not None:
        thickness = radius * thickness_factor
    else:
        thickness = None

    return CircularBorder(center=center, radius=r0, thickness=thickness)


@dataclass(kw_only=True, slots=True)
class RectangularBorder(Border):
    """Rectangular boundary."""

    corner_low: Vec2
    corner_high: Vec2

    def dist_to_inner_boundary(self, points: MatNx2) -> float:
        _max = amax(points, axis=0)
        _min = amin(points, axis=0)
        return min(amin(_min - self.corner_low), amin(self.corner_high - _max))


def rectangular_border(
    polygons: list[Polygon], inner_factor: float, thickness_factor: float | None = None
) -> RectangularBorder:
    """Compute the rectangular boundary."""
    center, lengths = smallest_rectangle(_get_vertices(polygons))

    r = float(norm(lengths))
    l0 = lengths + r * inner_factor
    if thickness_factor is not None:
        thickness = r * thickness_factor
    else:
        thickness = None

    return RectangularBorder(
        center=center,
        half_width=l0[0],
        half_height=l0[1],
        thickness=thickness,
    )


def _get_vertices(polygons: list[Polygon]) -> MatNx2:
    """Get the vertices."""
    return vstack([polygon.get_vertices() for polygon in polygons])
