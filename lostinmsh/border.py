"""Class for boundary."""


from dataclasses import dataclass
from typing import Optional

from numpy.linalg import norm
from numpy.typing import NDArray

from .smallest_boundary import smallest_circle, smallest_rectangle


@dataclass(kw_only=True, slots=True)
class Border:
    """Border class."""

    center: NDArray
    thickness: Optional[float] = None

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        """Sign distance to the inner boundary.

        It is positive is all the points are inside and it is negative
        if at least one point is outside.

        """
        raise NotImplementedError()


@dataclass(kw_only=True, slots=True)
class Circular(Border):
    """Circular boundary."""

    radius: float

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        """Sign distance to the inner boundary.

        It is positive is all the points are inside and it is negative
        if at least one point is outside.

        """
        return self.radius - norm(points - self.center, axis=1).max()


@dataclass(kw_only=True, slots=True)
class Rectangular(Border):
    """Rectangular boundary."""

    half_width: float
    half_height: float

    def dist_to_inner_boundary(self, points: NDArray) -> float:
        """Sign distance to the inner boundary.

        It is positive is all the points are inside and it is negative
        if at least one point is outside.

        """
        pts = points - self.center
        return min(
            self.half_width - pts[:, 0].max(), self.half_height - pts[:, 1].max()
        )


@dataclass(kw_only=True, slots=True)
class AutoBorder:
    """Auto border class.

    Attributes
    ----------
    border_factor : float
        a
    thickness_factor : Optional[float] = None
        b

    """

    border_factor: float
    thickness_factor: Optional[float] = None

    def get_border(self, points: NDArray) -> Border:
        """Get border."""
        raise NotImplementedError()


@dataclass(kw_only=True, slots=True)
class AutoCircular(AutoBorder):
    """Auto circular.

    Attributes
    ----------
    border_factor : float
        a
    thickness_factor : Optional[float] = None
        b

    """

    def get_border(self, points: NDArray) -> Circular:
        """Auto set.

        Parameters
        ----------
        points : NDArray
            list of points should be an array of shape (N, 2) with N ≥ 1.

        """
        center, radius = smallest_circle(points)

        r0 = radius * (1 + self.border_factor)
        if self.thickness_factor is not None:
            thickness = radius * self.thickness_factor
        else:
            thickness = None

        return Circular(center=center, radius=r0, thickness=thickness)


@dataclass(kw_only=True, slots=True)
class AutoRectangular(AutoBorder):
    """Auto circular."""

    def get_border(self, points: NDArray) -> Rectangular:
        """Auto set."""
        center, lengths = smallest_rectangle(points)

        r = float(norm(lengths))
        l0 = lengths + r * self.border_factor
        if self.thickness_factor is not None:
            thickness = r * self.thickness_factor
        else:
            thickness = None

        return Rectangular(
            center=center, half_width=l0[0], half_height=l0[1], thickness=thickness
        )
