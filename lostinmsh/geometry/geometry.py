from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Self

from numpy import inf

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

    def critical_interval(self: Self) -> tuple[float, float]:
        """Compute the critical interval of polygons.

        Returns
        -------
        tuple[float, float]
            Critical interval of the polygon.
        """

        a, b = (inf, -inf)
        for polygon in self.polygons:
            interval = polygon.critical_interval()
            a = min(a, interval[0])
            b = max(b, interval[1])

        return (a, b)

    def discrete_critical_interval(self: Self) -> tuple[float, float]:
        """Compute the discrete critical interval of polygons.

        Returns
        -------
        tuple[float, float]
            Discrete critical interval of the polygon.
        """

        a, b = (inf, -inf)
        for polygon in self.polygons:
            interval = polygon.discrete_critical_interval()
            a = min(a, interval[0])
            b = max(b, interval[1])

        return (a, b)
