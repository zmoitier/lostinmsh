# type: ignore

from pathlib import PurePath

ENABLE_MATPLOTLIB = True
ENABLE_MESHIO = True
try:
    import matplotlib.pyplot as plt
    import meshio
except ImportError:
    ENABLE_MATPLOTLIB = False
    ENABLE_MESHIO = False


def plot_mesh(filename: PurePath | str, *, ax=None) -> None:
    """Plot mesh from .msh file.

    Parameters
    ----------
    filename : PurePath | str
        Path to .msh file.
    """
    if ENABLE_MATPLOTLIB and ENABLE_MESHIO:
        _plot_mesh(filename, ax)
    else:
        raise ModuleNotFoundError(
            "You need to install matplotlib and meshio to use this function."
        )

    return None


def _plot_mesh(filename: PurePath | str, ax) -> None:
    """Plot mesh from .msh file."""
    if ax is None:
        _, ax = plt.subplots()

    mesh = meshio.read(filename)
    pts = mesh.points[:, :2]

    # Handle triangular elements of any order (triangle, triangle6, triangle10, etc.)
    cell_type = None
    triangles = None

    for key in mesh.cells_dict.keys():
        if key.startswith("triangle"):
            cell_type = key
            triangles = mesh.cells_dict[key][:, :3]
            break

    if cell_type is None or triangles is None:
        raise ValueError("No triangle elements found in mesh")

    triangle_tags = mesh.cell_data_dict["gmsh:physical"][cell_type]

    for name, (tag, dim) in mesh.field_data.items():
        if dim != 2:
            continue

        ax.triplot(
            pts[:, 0],
            pts[:, 1],
            triangles[triangle_tags == tag],
            linewidth=0.5,
            label=name,
        )

    ax.set_aspect("equal")
    ax.legend()

    return None
