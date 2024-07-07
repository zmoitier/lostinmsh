from fractions import Fraction
from sys import argv

import matplotlib.pyplot as plt
import numpy as np
import pytest

from lostinmsh.geometry import RationalAngle, elementary_angle


@pytest.mark.parametrize(
    "test_input,elem_ang",
    [
        (Fraction(1, 12), Fraction(1, 24)),
        (Fraction(2, 12), Fraction(1, 12)),
        (Fraction(3, 12), Fraction(1, 8)),
        (Fraction(4, 12), Fraction(1, 6)),
        (Fraction(5, 12), Fraction(1, 12)),
        (Fraction(6, 12), Fraction(1, 4)),
        (Fraction(7, 12), Fraction(1, 12)),
        (Fraction(8, 12), Fraction(1, 3)),
        (Fraction(9, 12), Fraction(1, 4)),
        (Fraction(10, 12), Fraction(1, 6)),
        (Fraction(11, 12), Fraction(1, 12)),
        (Fraction(12, 12), Fraction(1, 2)),
        (Fraction(13, 12), Fraction(1, 12)),
        (Fraction(14, 12), Fraction(1, 6)),
        (Fraction(15, 12), Fraction(1, 4)),
        (Fraction(16, 12), Fraction(1, 3)),
        (Fraction(17, 12), Fraction(1, 12)),
        (Fraction(18, 12), Fraction(1, 4)),
        (Fraction(19, 12), Fraction(1, 12)),
        (Fraction(20, 12), Fraction(1, 6)),
        (Fraction(21, 12), Fraction(1, 8)),
        (Fraction(22, 12), Fraction(1, 12)),
        (Fraction(23, 12), Fraction(1, 24)),
    ],
)
class TestAngle:
    def test_angle(self, test_input, elem_ang):
        a = RationalAngle(test_input)
        assert elementary_angle(a) == elem_ang


def arc(t_min: float, t_max: float, N: int):
    t = np.linspace(t_min, t_max, num=int(np.ceil(2 * np.pi * N / (t_max - t_min))))
    c, s = np.cos(t), np.sin(t)
    return ([0, *c], [0, *s])


def main(a: RationalAngle, e: RationalAngle) -> None:
    """Main function."""
    N = 32

    _, ax = plt.subplots(constrained_layout=True)
    ax.axis("equal")
    ax.grid(True, zorder=1)

    ax.fill(*arc(0, a.value, N), facecolor="C0", alpha=0.75, zorder=2)
    ax.fill(*arc(a.value, 2 * np.pi, N), facecolor="C1", alpha=0.75, zorder=2)

    K = 2 / e
    if K.denominator != 1:
        raise ValueError(K)

    for k in range(int(K)):
        ax.plot([0, np.cos(k * e.value)], [0, np.sin(k * e.value)], "k")

    plt.show()


if __name__ == "__main__":
    a = RationalAngle(int(argv[1]), int(argv[2]))
    e = RationalAngle(int(argv[3]), int(argv[4]))
    main(a, e)
