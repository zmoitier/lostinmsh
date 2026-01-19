from fractions import Fraction

import matplotlib.pyplot as plt
import numpy as np


def compute_pq(angle: float, max_denominator: int) -> tuple[int, int]:
    """Compute p and q for a given angle."""

    r = Fraction(angle / np.pi).limit_denominator(max_denominator)
    s = Fraction(r.numerator, 2 * r.denominator - r.numerator)
    p, q = s.numerator, s.denominator
    if ((p + q) % 2 == 1) or (p == 1) or (q == 1):
        p *= 2
        q *= 2

    return (p, q)


def main(max_dem: int) -> None:
    rat_set = set([Fraction(0, 1)])
    for n in range(1, max_dem + 1):
        for k in range(1, 2 * n):
            rat = Fraction(k, n)
            rat_set.add(rat)

    print(len(rat_set))

    angles = np.pi * np.array(sorted(rat_set), dtype=np.float64)

    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.grid()
    ax.plot(np.cos(angles), np.sin(angles), "o")
    plt.show()


if __name__ == "__main__":
    main(12)
