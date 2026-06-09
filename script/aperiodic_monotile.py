"""Regular polygon."""

from sys import argv

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(mesh_size: float) -> None:
    s3 = np.sqrt(3)
    vertices: list[list[float]] = [
        [0, 0],
        [0, s3],
        [1, s3],
        [3 / 2, 3 * s3 / 2],
        [3, s3],
        [3, 0],
        [4, 0],
        [9 / 2, -s3 / 2],
        [3, -s3],
        [3 / 2, -s3 / 2],
        [1, -s3],
        [-1, -s3],
        [-3 / 2, -s3 / 2],
    ]

    polygon = lsm.Polygon.from_vertices(vertices, "cavity")
    boundary = lsm.rectangular_boundary([polygon], 0.5, "background", 0.25, "PML")
    geometry = lsm.Geometry.from_polygon(polygon, boundary)

    print(f"         critical interval: {geometry.critical_interval()}")
    print(f"discrete critical interval: {geometry.discrete_critical_interval()}")

    lsm.plot_geometry(geometry)
    plt.show()

    lsm.mesh_unstructured(geometry, mesh_size, lsm.GmshOptions(show_gui=True))
    lsm.mesh_locally_structured(geometry, mesh_size, lsm.GmshOptions(show_gui=True))


if __name__ == "__main__":
    mesh_size = float(argv[1])

    main(mesh_size)
