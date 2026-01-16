"""Regular polygon."""

from sys import argv

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(mesh_size: float) -> None:
    a = np.pi / 8
    c, s = np.cos(a / 2), np.sin(a / 2)
    vertices = np.array([[0.0, 0.0], [c, s], [c, -s]])

    polygons = [
        lsm.Polygon.from_vertices(np.array([0.1, 0.0]) + vertices, "right"),
        lsm.Polygon.from_vertices(np.array([-0.1, 0.0]) - vertices, "left"),
    ]
    boundary = lsm.rectangular_boundary(polygons, 0.25, 0.25)
    geometry = lsm.Geometry.from_polygons(polygons, boundary)

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
    mesh_size = float(argv[1])

    main(mesh_size)
