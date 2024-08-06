"""Test."""

import numpy as np  # noqa: F401

import lostinmsh as lsm  # noqa: F401


def main() -> None:
    """Main."""
    a = np.array([[0, 0], [1, 2], [2, 4]])
    b = np.array([[0, 0], [1, 2], [2, 4]])
    print(np.vstack((a, b)))

    # t = np.linspace(0, 2 * np.pi, num=15, endpoint=False)
    # vertices = np.array([[x, y] for x, y in zip(np.cos(t), np.sin(t))])

    # polygons = [lsm.Polygon.from_vertices(vertices, "Cavity")]

    # border = lsm.AutoCircular(border_factor=0.3)
    # geometry = lsm.Geometry.from_polygons(polygons, border)

    # # lsm.mesh_unstructured(geometry, 0.25, lsm.GmshOptions(gui=True, terminal=True))
    # lsm.mesh_loc_struct(
    #     geometry,
    #     0.1,
    #     lsm.GmshOptions(
    #         gui=True,
    #         terminal=1,
    #         filename="mesh.msh",
    #         additional_options={"Mesh.MeshSizeMin": 0.1, "Mesh.MeshSizeMax": 0.1},
    #     ),
    # )


if __name__ == "__main__":
    main()
