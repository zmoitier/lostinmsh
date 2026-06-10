# type: ignore

from numpy import pi

from ..geometry import CircularBoundary, Geometry, Polygon, RectangularBoundary

ENABLE_MATPLOTLIB = True
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle as mpl_Circle
    from matplotlib.patches import Polygon as mpl_Polygon
    from matplotlib.patches import Rectangle as mpl_Rectangle
except ImportError:
    ENABLE_MATPLOTLIB = False


def plot_polygon(polygon: Polygon, *, ax=None, show_pq=False) -> None:
    """Plot polygon.

    Parameters
    ----------
    polygon : Polygon
    ax : plt.Axes, optional, default=None
    show_pq : bool, optional, default=False
    """
    if ENABLE_MATPLOTLIB:
        _plot_polygon(polygon, ax, show_pq)
    else:
        raise ModuleNotFoundError(
            "You need to install matplotlib to use this function."
        )

    return None


def _plot_polygon(polygon: Polygon, ax, show_pq) -> None:
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

    if show_pq:
        for v, c in zip(polygon.vertices, polygon.corners):
            ax.text(
                v[0],
                v[1],
                f"{c.angle / pi:.2f}π\n({c.p}, {c.q})",
                color="C1",
                va="center",
                ha="center",
                bbox=dict(
                    boxstyle="round", edgecolor="black", facecolor="white", alpha=0.75
                ),
            )

    ax.axis("equal")
    ax.grid(zorder=1)
    ax.legend(loc=1)

    return None


def plot_geometry(geometry: Geometry, ax=None) -> None:
    """Plot geometry.

    Parameters
    ----------
    geometry : Geometry
    ax : plt.Axes, optional, default=None
    """
    if ENABLE_MATPLOTLIB:
        _plot_geometry(geometry, ax)
    else:
        raise ModuleNotFoundError(
            "You need to install matplotlib to use this function."
        )

    return None


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

    return None


def _add_circ_boundary(ax, circ: CircularBoundary, options_bak, options_thk) -> None:
    """Add circular boundary."""
    ax.plot([circ.center[0]], [circ.center[1]], "ko", zorder=5)
    ax.add_patch(mpl_Circle(circ.center, circ.radius, **options_bak))

    if circ.thickness is not None:
        ax.add_patch(
            mpl_Circle(circ.center, circ.radius + circ.thickness, **options_thk)
        )


def _add_rect_boundary(ax, rect: RectangularBoundary, options_bak, options_thk) -> None:
    """Add rectangular boundary."""
    a, b = rect.corner_low, rect.corner_high
    d = b - a

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
