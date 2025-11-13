# type: ignore

from .geometry import (
    CircularBoundary,
    Geometry,
    Polygon,
    RationalAngle,
    RectangularBoundary,
)

ENABLE_PLOT = False
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle as mpl_Circle
    from matplotlib.patches import Polygon as mpl_Polygon
    from matplotlib.patches import Rectangle as mpl_Rectangle

    ENABLE_PLOT = True

except ImportError:
    pass


def plot_polygon(polygon: Polygon, *, ax=None, show_angle=True) -> None:
    """Plot polygon.

    Parameters
    ----------
    polygon : Polygon
    ax : plt.Axes, optional, default=None
    show_angle : bool, optional, default=True
    """

    if ENABLE_PLOT:
        _plot_polygon(polygon, ax, show_angle)
    else:
        raise ModuleNotFoundError(
            "You need to install matplotlib to use this function."
        )


def _plot_polygon(polygon: Polygon, ax, show_angle) -> None:
    """Plot polygon."""

    if ax is None:
        _, ax = plt.subplots()

    ax.add_patch(
        mpl_Polygon(
            polygon.vertices,
            linewidth=2,
            color="C0",
            fill=False,
            zorder=2,
            label=polygon.name,
        )
    )

    if show_angle:
        for v, a in zip(polygon.vertices, polygon.angles):
            ax.text(
                v[0],
                v[1],
                latex(a),
                color="C1",
                va="center",
                ha="center",
                bbox=dict(boxstyle="round", edgecolor="black", facecolor="white"),
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
    ax : plt.Axes, optional, default=None
    """

    if ENABLE_PLOT:
        _plot_geometry(geometry, ax)
    else:
        raise ModuleNotFoundError(
            "You need to install matplotlib to use this function."
        )


def _plot_geometry(geometry: Geometry, ax=None) -> None:
    """Plot geometry."""

    if ax is None:
        _, ax = plt.subplots()

    k = len(geometry.polygons)
    for i, polygon in enumerate(geometry.polygons):
        ax.add_patch(
            mpl_Polygon(
                polygon.vertices,
                linewidth=2,
                color=f"C{i}",
                alpha=0.75,
                zorder=4,
                label=polygon.name,
            )
        )

    options_bak = {
        "linewidth": 2,
        "linestyle": "--",
        "edgecolor": "k",
        "facecolor": f"C{k + 1}",
        "alpha": 0.75,
        "zorder": 3,
        "label": geometry.boundary.background_name,
    }
    options_thk = {
        "linewidth": 2,
        "linestyle": "-.",
        "edgecolor": "k",
        "facecolor": f"C{k + 2}",
        "alpha": 0.75,
        "zorder": 2,
        "label": geometry.boundary.thickness_name,
    }

    if isinstance(geometry.boundary, CircularBoundary):
        _add_circ_boundary(ax, geometry.boundary, options_bak, options_thk)

    elif isinstance(geometry.boundary, RectangularBoundary):
        _add_rect_boundary(ax, geometry.boundary, options_bak, options_thk)

    else:
        raise ValueError("Unknown boundary shape.")

    ax.axis("equal")
    ax.grid(zorder=1)
    ax.legend(loc=1)


def _add_circ_boundary(ax, circ: CircularBoundary, options_bak, options_thk):
    """Add circular boundary."""

    ax.plot([circ.center[0]], [circ.center[1]], "ko", zorder=5)
    ax.add_patch(mpl_Circle(circ.center, circ.radius, **options_bak))

    if circ.thickness is not None:
        ax.add_patch(
            mpl_Circle(circ.center, circ.radius + circ.thickness, **options_thk)
        )


def _add_rect_boundary(ax, rect: RectangularBoundary, options_bak, options_thk):
    """Add rectangular boundary."""

    a, b = rect.corner_low, rect.corner_high
    c = (a + b) / 2
    d = b - a

    ax.plot([c[0]], [c[1]], "ko", zorder=5)
    ax.add_patch(mpl_Rectangle(a, d[0], d[1], **options_bak))

    if rect.thickness is not None:
        ax.add_patch(
            mpl_Rectangle(
                a - rect.thickness,
                d[0] + 2 * rect.thickness,
                d[1] + 2 * rect.thickness,
                **options_thk,
            )
        )
