from fractions import Fraction

import matplotlib.pyplot as plt
import numpy as np


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
