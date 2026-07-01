"""Tests for the aperiodic monotile example."""

import matplotlib.pyplot as plt
import numpy as np

import lostinmsh as lsm


def main(mesh_size: float) -> None:
    s3 = np.sqrt(3)
    vertices: list[list[float]] = [
        [0, 0],
        [0, s3],
        [1, s3],
        [3 / 2, 3 * s3 / 2],
        [3, s3],
        [3, 0],
        [4, 0],
        [9 / 2, -s3 / 2],
        [3, -s3],
        [3 / 2, -s3 / 2],
        [1, -s3],
        [-1, -s3],
        [-3 / 2, -s3 / 2],
    ]

    polygon = lsm.Polygon.from_vertices(vertices, "cavity")
    lsm.plot_polygon(polygon)
    plt.close()

    for boundary in [
        lsm.circular_boundary([polygon], 0.25, "background"),
        lsm.circular_boundary([polygon], 0.25, "background", 0.25, "PML"),
    ]:
        geometry = lsm.Geometry.from_polygon(polygon, boundary)

        assert geometry.critical_interval() is not None
        assert geometry.discrete_critical_interval() is not None

        lsm.plot_geometry(geometry)
        plt.close()

        filename = lsm.mesh_unstructured(
            geometry,
            mesh_size,
            lsm.GmshOptions(
                filename="tests/aperiodic_monotile_unst.msh", element_order=2
            ),
        )
        assert filename is not None
        lsm.plot_mesh(filename)
        plt.close()

        filename = lsm.mesh_locally_structured(
            geometry,
            mesh_size,
            lsm.GmshOptions(
                filename="tests/aperiodic_monotile_lost.msh", renumber_nodes=None
            ),
        )
        assert filename is not None
        lsm.plot_mesh(filename)
        plt.close()

    return None


def test_aperiodic_monotile() -> None:
    main(0.25)


if __name__ == "__main__":
    test_aperiodic_monotile()
