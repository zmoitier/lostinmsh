"""Tests for the cocotte fleche example."""

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(mesh_size: float) -> None:
    cocotte = np.array([[2, 0], [3, 1], [3, 2], [1, 2], [1, 3], [0, 2], [1, 1], [2, 1]])
    fleche = np.array([[2, 0], [2, 1], [3, 1], [2, 2], [1, 2], [1, 3], [0, 3], [0, 2]])

    polygons = [
        lsm.Polygon.from_vertices(cocotte - np.array([3.2, 0]), "cocotte"),
        lsm.Polygon.from_vertices(fleche + np.array([0.2, 0]), "fleche"),
    ]

    for boundary in [
        lsm.rectangular_boundary(polygons, 0.25, "background"),
        lsm.rectangular_boundary(polygons, 0.25, "background", 0.25, "PML"),
    ]:
        geometry = lsm.Geometry.from_polygons(polygons, boundary)

        assert geometry.critical_interval() is not None
        assert geometry.discrete_critical_interval() is not None

        lsm.plot_geometry(geometry)
        plt.close()

        filename = lsm.mesh_unstructured(
            geometry,
            mesh_size,
            lsm.GmshOptions(filename="tests/cocotte_fleche_unst.msh"),
        )
        assert filename is not None
        lsm.plot_mesh(filename)
        plt.close()

        filename = lsm.mesh_locally_structured(
            geometry,
            mesh_size,
            lsm.GmshOptions(filename="tests/cocotte_fleche_lost.msh"),
        )
        assert filename is not None
        lsm.plot_mesh(filename)
        plt.close()

    return None


def test_cocotte_fleche() -> None:
    main(0.25)


if __name__ == "__main__":
    test_cocotte_fleche()
