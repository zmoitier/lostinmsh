"""Geometry class."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Self

# from scipy.spatial.distance import pdist
from .boundary import ExteriorBoundary
from .polygon import Polygon


@dataclass(kw_only=True, slots=True)
class Geometry:
    """Geometry class.

    Attributes
    ----------
    polygons : list[Polygon]
    boundary : ExteriorBoundary
    """

    polygons: list[Polygon]
    boundary: ExteriorBoundary

    @classmethod
    def from_polygon(cls, polygon: Polygon, boundary: ExteriorBoundary) -> Geometry:
        """Create a geometry from a polygon.

        Parameters
        ----------
        polygon : Polygon
        boundary : ExteriorBoundary
        """

        return cls(polygons=[polygon], boundary=boundary)

    @classmethod
    def from_polygons(
        cls, polygons: Iterable[Polygon], boundary: ExteriorBoundary
    ) -> Geometry:
        """Create a geometry from polygons.

        Parameters
        ----------
        polygon : Iterable[Polygon]
        boundary: ExteriorBoundary
        """

        return cls(polygons=list(polygons), boundary=boundary)

    def critical_interval(self: Self) -> dict[str, tuple[Fraction, Fraction]]:
        """Get the critical interval."""
        return {polygon.name: polygon.critical_interval() for polygon in self.polygons}

    # def max_corner_radius(self) -> float:
    #     """Maximum corner radius."""
    #     points = vstack([polygon.get_vertices() for polygon in self.polygons])
    #     return min(min_dist(points) / 2, self.border.dist_to_inner_boundary(points))
