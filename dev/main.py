"""Main."""

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main() -> None:
    """Main."""

    # vertices: list[list[float]] = [[0, 0], [1, 0], [0, 1]]

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
    geometry = lsm.Geometry.from_polygons([polygon], boundary)

    # lsm.plot_geometry(geometry)
    # plt.show()

    lsm.mesh_unstructured(
        geometry,
        0.1,
        lsm.GmshOptions(
            show_gui=True,
            filename="mesh.msh",
            additional_options={"Mesh.MeshSizeMin": 0.1, "Mesh.MeshSizeMax": 0.1},
            renumber_nodes=None,
        ),
    )

    # lsm.mesh_loc_struct(
    #     geometry,
    #     0.1,
    #     lsm.GmshOptions(
    #         element_order=2,
    #         show_gui=False,
    #         show_terminal_output=True,
    #         filename="mesh.msh",
    #         additional_options={"Mesh.MeshSizeMin": 0.1, "Mesh.MeshSizeMax": 0.1},
    #     ),
    # )


if __name__ == "__main__":
    main()
