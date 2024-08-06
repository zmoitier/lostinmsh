"""Class for boundary."""

from dataclasses import dataclass

from numpy import asarray, vstack
from numpy.linalg import norm
from numpy.typing import NDArray

from .polygon import MatNx2, Polygon
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
class CircularBorder(Border):
    """Circular boundary."""

    radius: float

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        return self.radius - norm(points - asarray(self.center), axis=1).max()


@dataclass(kw_only=True, slots=True)
class RectangularBorder(Border):
    """Rectangular boundary."""

    half_width: float
    half_height: float

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        pts = points - self.center
        return min(
            self.half_width - pts[:, 0].max(), self.half_height - pts[:, 1].max()
        )


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

    return CircularBorder(center=(center[0], center[1]), radius=r0, thickness=thickness)


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
        center=(center[0], center[1]),
        half_width=l0[0],
        half_height=l0[1],
        thickness=thickness,
    )


def _get_vertices(polygons: list[Polygon]) -> MatNx2:
    """Get the vertices."""
    return vstack([polygon.get_vertices() for polygon in polygons])
