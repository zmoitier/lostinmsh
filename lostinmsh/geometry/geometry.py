"""Geometry class."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Union

from numpy import asarray, vstack

from .border import AutoBorder, Border
from .closest_points import min_dist
from .polygon import Polygon


@dataclass(kw_only=True, slots=True)
class Geometry:
    """Geometry class.

    Attributes
    ----------
    polygons : list[Polygon]
    border : Border
    """

    polygons: list[Polygon]
    border: Border

    @classmethod
    def from_polygon(
        cls, polygon: Polygon, border: Union[Border, AutoBorder]
    ) -> Geometry:
        """Create a geometry from a polygon.

        Parameters
        ----------
        polygon : Polygon
        border : Union[Border, AutoBorder]
        """

        if isinstance(border, AutoBorder):
            return cls(
                polygons=[polygon], border=border.get_border(polygon.get_vertices())
            )

        if isinstance(border, Border):
            return cls(polygons=[polygon], border=border)

        raise ValueError("Unknown border shape.")

    @classmethod
    def from_polygons(
        cls, polygons: Iterable[Polygon], border: Union[Border, AutoBorder]
    ) -> Geometry:
        """Create a geometry from polygons.

        Parameters
        ----------
        polygon : Iterable[Polygon]
        border : Union[Border, AutoBorder]
        """

        points = vstack([polygon.get_vertices() for polygon in polygons])

        if isinstance(border, AutoBorder):
            return cls(polygons=list(polygons), border=border.get_border(points))

        if isinstance(border, Border):
            return cls(polygons=list(polygons), border=border)

        raise ValueError("Unknown border shape.")

    def make_center_origin(self):
        """Do a translation to set the center at (0, 0)."""
        center = self.border.center

        for polygon in self.polygons:
            polygon.translate(-center)

        self.border.center = asarray([0, 0])

    def critical_interval(self) -> dict[str, tuple[Fraction, Fraction]]:
        """Get the critical interval."""
        return {polygon.name: polygon.critical_interval() for polygon in self.polygons}

    def max_corner_radius(self) -> float:
        """Maximum corner radius."""
        points = vstack([polygon.get_vertices() for polygon in self.polygons])
        return min(min_dist(points) / 2, self.border.dist_to_inner_boundary(points))
