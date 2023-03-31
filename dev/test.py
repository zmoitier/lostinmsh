"""Test."""

import numpy as np

import lostinmsh as lsm


def main() -> None:
    """Main."""
    vertices = [[0, 0], [1, 0], [0, 1]]
    polygon = lsm.Polygon.from_vertices(vertices, "Cavity")

    border = lsm.Circular(center=np.array([1 / 3, 1 / 3]), radius=1, thickness=0.2)
    geometry = lsm.Geometry.from_polygon(polygon, border)

    lsm.mesh(geometry, 0.1, lsm.GmshOptions(gui=True, terminal=True))
    # lsm.mesh_loc_struct(geometry, 0.1, lsm.GmshOptions(gui=True))


if __name__ == "__main__":
    main()
