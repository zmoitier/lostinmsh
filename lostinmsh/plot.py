"""Plot polygon and geometry."""

from numpy import pi

from .geometry import (
    CircularBorder,
    Geometry,
    Polygon,
    RationalAngle,
    RectangularBorder,
    smallest_rectangle,
)
from .mesh import C_PML, C_POLYGON, C_VACUUM, to_global

ENABLE_PLOT = True
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle as mpl_Circle
    from matplotlib.patches import Polygon as mpl_Polygon
    from matplotlib.patches import Rectangle as mpl_Rectangle
except ImportError:
    ENABLE_PLOT = False


def plot_polygon(polygon: Polygon, ax=None) -> None:
    """Plot polygon.

    Parameters
    ----------
    polygon : Polygon
    ax : plt.Axes, optional
    """
    if ENABLE_PLOT:
        _plot_polygon(polygon, ax=ax)
    else:
        raise ModuleNotFoundError(
            "You need to install matplotlib to use this function."
        )


def _plot_polygon(polygon: Polygon, ax=None) -> None:
    """Plot polygon."""
    if ax is None:
        _, ax = plt.subplots()

    ax.add_patch(
        mpl_Polygon(
            polygon.get_vertices(),
            linewidth=2,
            fill=False,
            color=C_POLYGON.mpl,
            zorder=2,
            label=polygon.name,
        )
    )

    l_min = polygon.lengths.min()
    for corner in polygon.corners:
        if corner.angle < 1:
            angle = pi + corner.angle.value / 2
        else:
            angle = corner.angle.value / 2
        pts = to_global(corner, 0.15 * l_min, angle)
        ax.text(pts[0], pts[1], latex(corner.angle), va="center", ha="center")

    center, lengths = smallest_rectangle(polygon.get_vertices())
    lengths *= 1.2
    ax.add_patch(
        mpl_Rectangle(
            center - lengths, 2 * lengths[0], 2 * lengths[1], fill=False, linewidth=0
        )
    )

    ax.axis("equal")
    ax.grid(zorder=1)
    ax.legend(loc=1)


def latex(angle: RationalAngle) -> str:
    """Get latex representation."""

    if angle.numerator == 0:
        return r"$0$"

    if angle.numerator == 1:
        str_num = ""
    elif angle.numerator == -1:
        str_num = "-"
    else:
        str_num = f"{angle.numerator}"

    return rf"$\dfrac{{{str_num}\pi}}{{{angle.denominator}}}$"


def plot_geometry(geometry: Geometry, ax=None) -> None:
    """Plot geometry.

    Parameters
    ----------
    geometry : Geometry
    ax : plt.Axes, optional
    """
    if ENABLE_PLOT:
        _plot_geometry(geometry, ax=ax)
    else:
        raise ModuleNotFoundError(
            "You need to install matplotlib to use this function."
        )


def _plot_geometry(geometry: Geometry, ax=None) -> None:
    """Plot geometry."""
    if ax is None:
        _, ax = plt.subplots()

    for polygon in geometry.polygons:
        ax.add_patch(
            mpl_Polygon(
                polygon.get_vertices(),
                linewidth=2,
                color=C_POLYGON.mpl,
                zorder=4,
                label=polygon.name,
            )
        )

    ax.plot([geometry.border.center[0]], [geometry.border.center[1]], "ko")

    options_vac = {
        "linewidth": 2,
        "linestyle": "--",
        "edgecolor": "k",
        "facecolor": C_VACUUM.mpl,
        "zorder": 3,
        "label": "Vaccum",
    }
    options_pml = {
        "linewidth": 2,
        "linestyle": "-.",
        "edgecolor": "k",
        "facecolor": C_PML.mpl,
        "zorder": 2,
        "label": "PML",
    }

    if isinstance(geometry.border, CircularBorder):
        _add_circular(ax, geometry.border, options_vac, options_pml)
    elif isinstance(geometry.border, RectangularBorder):
        _add_rectangular(ax, geometry.border, options_vac, options_pml)
    else:
        raise ValueError("Unknown border shape.")

    ax.axis("equal")
    ax.grid(zorder=1)
    ax.legend(loc=1)


def _add_circular(ax, circ: CircularBorder, options_vac, options_pml):
    """Add circular border."""
    ax.add_patch(mpl_Circle(circ.center, circ.radius, **options_vac))

    if circ.thickness is not None:
        ax.add_patch(
            mpl_Circle(circ.center, circ.radius + circ.thickness, **options_pml)
        )


def _add_rectangular(ax, rect: RectangularBorder, options_vac, options_pml):
    """Add circular border."""
    x, y = rect.center
    ax.add_patch(
        mpl_Rectangle(
            (x - rect.half_width, y - rect.half_height),
            2 * rect.half_width,
            2 * rect.half_height,
            **options_vac,
        )
    )

    if rect.thickness is not None:
        ax.add_patch(
            mpl_Rectangle(
                (
                    x - rect.half_width - rect.thickness,
                    y - rect.half_height - rect.thickness,
                ),
                2 * (rect.half_width + rect.thickness),
                2 * (rect.half_height + rect.thickness),
                **options_pml,
            )
        )
