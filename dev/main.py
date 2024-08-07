"""Main."""

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main() -> None:
    """Main."""
    t = np.linspace(0, 2 * np.pi, num=4, endpoint=False)
    vertices = np.array([[x, y] for x, y in zip(np.cos(t), np.sin(t))])

    polygons = [lsm.Polygon.from_vertices(vertices, "Cavity")]

    border = lsm.AutoCircular(border_factor=0.3, thickness_factor=0.2)
    geometry = lsm.Geometry.from_polygons(polygons, border)

    # lsm.mesh_unstructured(
    #     geometry,
    #     0.1,
    #     lsm.GmshOptions(
    #         element_order=2,
    #         gui=False,
    #         terminal=True,
    #         filename="mesh.msh",
    #         additional_options={"Mesh.MeshSizeMin": 0.1, "Mesh.MeshSizeMax": 0.1},
    #     ),
    # )

    lsm.mesh_loc_struct(
        geometry,
        0.1,
        lsm.GmshOptions(
            element_order=2,
            gui=False,
            terminal=True,
            filename="mesh.msh",
            additional_options={"Mesh.MeshSizeMin": 0.1, "Mesh.MeshSizeMax": 0.1},
        ),
    )


if __name__ == "__main__":
    main()
