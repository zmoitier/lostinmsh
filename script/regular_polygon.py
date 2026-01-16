"""Regular polygon."""

from sys import argv

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(nb_side: int, mesh_size: float) -> None:
    t = np.linspace(0, 2 * np.pi, nb_side, endpoint=False)
    vertices = np.vstack((np.cos(t), np.sin(t))).T

    polygon = lsm.Polygon.from_vertices(vertices, "cavity")
    boundary = lsm.circular_boundary([polygon], 0.25, 0.25)
    geometry = lsm.Geometry.from_polygon(polygon, boundary)

    lsm.plot_geometry(geometry)
    plt.show()

    lsm.mesh_unstructured(
        geometry,
        mesh_size,
        lsm.GmshOptions(
            element_order=1,
            # filename="mesh.msh",
            additional_options={
                "Mesh.MeshSizeMin": mesh_size,
                "Mesh.MeshSizeMax": mesh_size,
            },
            show_gui=True,
        ),
    )

    lsm.mesh_loc_struct(
        geometry,
        mesh_size,
        lsm.GmshOptions(
            element_order=1,
            # filename="mesh.msh",
            additional_options={
                "Mesh.MeshSizeMin": mesh_size,
                "Mesh.MeshSizeMax": mesh_size,
            },
            show_gui=True,
        ),
    )


if __name__ == "__main__":
    nb_side = int(argv[1])
    mesh_size = float(argv[2])

    main(nb_side, mesh_size)
