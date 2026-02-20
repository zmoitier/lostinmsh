"""Regular polygon."""

from sys import argv

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(nb_side: int, mesh_size: float) -> None:
    t = np.linspace(0, 2 * np.pi, nb_side, endpoint=False)
    vertices = np.vstack((np.cos(t), np.sin(t))).T

    polygon = lsm.Polygon.from_vertices(vertices, "cavity")
    boundary = lsm.circular_boundary([polygon], 0.25, "background", 0.25, "PML")
    geometry = lsm.Geometry.from_polygon(polygon, boundary)

    print(f"         critical interval: {geometry.critical_interval()}")
    print(f"discrete critical interval: {geometry.discrete_critical_interval()}")

    lsm.plot_geometry(geometry)
    plt.show()

    lsm.mesh_unstructured(geometry, mesh_size, lsm.GmshOptions(show_gui=True))
    lsm.mesh_loc_struct(geometry, mesh_size, lsm.GmshOptions(show_gui=True))


if __name__ == "__main__":
    nb_side = int(argv[1])
    mesh_size = float(argv[2])

    main(nb_side, mesh_size)
