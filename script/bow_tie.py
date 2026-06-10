"""Regular polygon."""

from sys import argv

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(mesh_size: float) -> None:
    a = 3 * np.pi / 4
    c, s = np.cos(a / 2), np.sin(a / 2)
    vertices = np.array([[0.0, 0.0], [c, s], [c, -s]])

    polygons = [
        lsm.Polygon.from_vertices(np.array([0.1, 0.0]) + vertices, "right"),
        lsm.Polygon.from_vertices(np.array([-0.1, 0.0]) - vertices, "left"),
    ]
    boundary = lsm.rectangular_boundary(polygons, 0.5, "background", 0.25, "PML")
    geometry = lsm.Geometry.from_polygons(polygons, boundary)

    print(f"         critical interval: {geometry.critical_interval()}")
    print(f"discrete critical interval: {geometry.discrete_critical_interval()}")

    lsm.plot_geometry(geometry)
    plt.show()

    lsm.mesh_unstructured(geometry, mesh_size, lsm.GmshOptions(show_gui=True))
    lsm.mesh_locally_structured(geometry, mesh_size, lsm.GmshOptions(show_gui=True))


if __name__ == "__main__":
    mesh_size = float(argv[1])

    main(mesh_size)
