"""Regular polygon."""

from sys import argv

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(mesh_size: float) -> None:
    vertices: list[list[float]] = [
        [0, 0],
        [0, np.sqrt(3)],
        [1, np.sqrt(3)],
        [3 / 2, 3 * np.sqrt(3) / 2],
        [3, np.sqrt(3)],
        [3, 0],
        [4, 0],
        [9 / 2, -np.sqrt(3) / 2],
        [3, -np.sqrt(3)],
        [3 / 2, -np.sqrt(3) / 2],
        [1, -np.sqrt(3)],
        [-1, -np.sqrt(3)],
        [-3 / 2, -np.sqrt(3) / 2],
    ]

    polygon = lsm.Polygon.from_vertices(vertices, "cavity")
    boundary = lsm.rectangular_boundary([polygon], 0.25, 0.25)
    geometry = lsm.Geometry.from_polygon(polygon, boundary)

    lsm.plot_geometry(geometry)
    plt.show()

    lsm.mesh_unstructured(
        geometry,
        mesh_size,
        lsm.GmshOptions(
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
    mesh_size = float(argv[1])

    main(mesh_size)
