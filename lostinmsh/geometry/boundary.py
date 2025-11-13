from dataclasses import dataclass

from numpy import amax, amin, inf, vstack
from numpy.linalg import norm

from ..type_alias import MatNx2, Vec2
from .polygon import Polygon
from .smallest_boundary import smallest_circle, smallest_rectangle


@dataclass(kw_only=True, slots=True)
class ExteriorBoundary:
    """Exterior boundary class.

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
    thickness_name: str = "thickness"

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
class CircularBoundary(ExteriorBoundary):
    """Circular boundary.

    Attributes
    ----------
    center : Vec2
        Center of the circle.
    radius : float
        Radius of the circle.
    background_name : str
        Name of the background.
    thickness : float, optional
        Thickness of the border.
    thickness_name : str
        Name of the thickness.
    """

    center: Vec2
    radius: float

    def dist_to_inner_boundary(self, points: MatNx2) -> float:
        return self.radius - norm(points - self.center, axis=1).max()


def circular_boundary(
    polygons: list[Polygon],
    inner_factor: float,
    thickness_factor: float | None = None,
    background_name: str = "background",
    thickness_name: str = "thickness",
) -> CircularBoundary:
    """Compute the circular boundary.

    Parameters
    ----------
    polygons : list[Polygon]
    inner_factor : float
    thickness_factor : float | None, optional, default None
    background_name : str, optional, default "background"
    thickness_name : str, optional, default "thickness"

    Returns
    -------
    CircularBoundary
    """

    center, radius = smallest_circle(_get_vertices(polygons))

    r0 = float(radius * (1 + inner_factor))

    if thickness_factor is not None:
        thickness = float(radius * thickness_factor)
    else:
        thickness = None

    return CircularBoundary(
        center=center,
        radius=r0,
        background_name=background_name,
        thickness=thickness,
        thickness_name=thickness_name,
    )


@dataclass(kw_only=True, slots=True)
class RectangularBoundary(ExteriorBoundary):
    """Rectangular boundary.

    Attributes
    ----------
    corner_low : Vec2
        Lower left corner of the rectangle.
    corner_high : Vec2
        Higher right corner of the rectangle.
    background_name : str
        Name of the background.
    thickness : float, optional
        Thickness of the border.
    thickness_name : str
        Name of the thickness.
    """

    corner_low: Vec2
    corner_high: Vec2

    def dist_to_inner_boundary(self, points: MatNx2) -> float:
        _max = amax(points, axis=0)
        _min = amin(points, axis=0)
        return min(amin(_min - self.corner_low), amin(self.corner_high - _max))


def rectangular_boundary(
    polygons: list[Polygon],
    inner_factor: float,
    thickness_factor: float | None = None,
    background_name: str = "background",
    thickness_name: str = "thickness",
) -> RectangularBoundary:
    """Compute the rectangular boundary.

    Parameters
    ----------
    polygons : list[Polygon]
    inner_factor : float
    thickness_factor : float | None, optional, default None
    background_name : str, optional, default "background"
    thickness_name : str, optional, default "thickness"

    Returns
    -------
    RectangularBoundary
    """

    corner_low, corner_high = smallest_rectangle(_get_vertices(polygons))
    r = float(norm(corner_high - corner_low, ord=inf) * inner_factor / 2)

    if thickness_factor is not None:
        thickness = r * thickness_factor
    else:
        thickness = None

    d = r * inner_factor
    return RectangularBoundary(
        corner_low=corner_low - d,
        corner_high=corner_high + d,
        background_name=background_name,
        thickness=thickness,
        thickness_name=thickness_name,
    )


def _get_vertices(polygons: list[Polygon]) -> MatNx2:
    """Get the vertices of polygons."""

    return vstack([polygon.vertices for polygon in polygons])
