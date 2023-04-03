"""Test."""

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main() -> None:
    """Main."""
    vertices = np.array([[0, 0], [1, 0], [0, 1]])
    shift = np.array([1, 0])

    polygons = [
        lsm.Polygon.from_vertices(vertices - shift, "Cavity"),
        lsm.Polygon.from_vertices(vertices + shift, "Cavity"),
    ]

    border = lsm.AutoCircular(border_factor=0.3, thickness_factor=0.125)
    geometry = lsm.Geometry.from_polygons(polygons, border)

    # lsm.mesh_unstructured(geometry, 0.25, lsm.GmshOptions(gui=True, terminal=True))
    lsm.mesh_loc_struct(
        geometry, 0.25, lsm.GmshOptions(gui=True, terminal=1, filename="mesh.msh")
    )


if __name__ == "__main__":
    main()
