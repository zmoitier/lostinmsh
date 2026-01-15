"""Main."""

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main() -> None:
    """Main."""

    vertices: list[list[float]] = [[0, 0], [1, 0], [0, 1]]
    # vertices: list[list[float]] = [
    #     [1, 0],
    #     [-0.5, np.sqrt(3) / 2],
    #     [-0.5, -np.sqrt(3) / 2],
    # ]

    # vertices: list[list[float]] = [
    #     [0, 0],
    #     [0, np.sqrt(3)],
    #     [1, np.sqrt(3)],
    #     [3 / 2, 3 * np.sqrt(3) / 2],
    #     [3, np.sqrt(3)],
    #     [3, 0],
    #     [4, 0],
    #     [9 / 2, -np.sqrt(3) / 2],
    #     [3, -np.sqrt(3)],
    #     [3 / 2, -np.sqrt(3) / 2],
    #     [1, -np.sqrt(3)],
    #     [-1, -np.sqrt(3)],
    #     [-3 / 2, -np.sqrt(3) / 2],
    # ]

    polygon = lsm.Polygon.from_vertices(vertices, "cavity")
    boundary = lsm.circular_boundary([polygon], 0.25, 0.25)
    # boundary = lsm.rectangular_boundary([polygon], 0.25, 0.25)
    geometry = lsm.Geometry.from_polygon(polygon, boundary)

    # lsm.plot_geometry(geometry)
    # plt.show()

    h = 0.05

    lsm.mesh_unstructured(
        geometry,
        h,
        lsm.GmshOptions(
            # filename="mesh.msh",
            additional_options={"Mesh.MeshSizeMin": h, "Mesh.MeshSizeMax": h},
            renumber_nodes=None,
            show_gui=True,
            show_terminal_output=False,
        ),
    )

    lsm.mesh_loc_struct(
        geometry,
        h,
        lsm.GmshOptions(
            element_order=1,
            # filename="mesh.msh",
            additional_options={"Mesh.MeshSizeMin": h, "Mesh.MeshSizeMax": h},
            renumber_nodes=None,
            show_gui=True,
            show_terminal_output=False,
        ),
    )


if __name__ == "__main__":
    main()
