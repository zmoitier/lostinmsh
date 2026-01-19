"""Regular polygon."""

from sys import argv

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(mesh_size: float) -> None:
    cocotte = np.array([[2, 0], [3, 1], [3, 2], [1, 2], [1, 3], [0, 2], [1, 1], [2, 1]])
    fleche = np.array([[2, 0], [2, 1], [3, 1], [2, 2], [1, 2], [1, 3], [0, 3], [0, 2]])

    polygons = [
        lsm.Polygon.from_vertices(cocotte - np.array([3.2, 0]), "cocotte"),
        lsm.Polygon.from_vertices(fleche + np.array([0.2, 0]), "fleche"),
    ]
    boundary = lsm.rectangular_boundary(polygons, 0.25, 0.25)
    geometry = lsm.Geometry.from_polygons(polygons, boundary)

    print(f"         critical interval: {geometry.critical_interval()}")
    print(f"discrete critical interval: {geometry.discrete_critical_interval()}")

    lsm.plot_geometry(geometry)
    plt.show()

    lsm.mesh_unstructured(geometry, mesh_size, lsm.GmshOptions(show_gui=True))
    lsm.mesh_loc_struct(geometry, mesh_size, lsm.GmshOptions(show_gui=True))


if __name__ == "__main__":
    mesh_size = float(argv[1])

    main(mesh_size)
