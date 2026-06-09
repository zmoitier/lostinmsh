from fractions import Fraction

import matplotlib.pyplot as plt
import numpy as np


def compute_pq_frac(angle: float, max_denominator: int) -> tuple[int, int]:
    """Compute p and q for a given angle."""
    r = Fraction(angle / np.pi).limit_denominator(max_denominator)
    if r.numerator == 0:
        r = Fraction(1, max_denominator)

    s = Fraction(r.numerator, 2 * r.denominator - r.numerator)
    p, q = s.numerator, s.denominator
    if ((p + q) % 2 == 1) or (p == 1) or (q == 1):
        p *= 2
        q *= 2

    return (p, q)


def compute_pq_min(angle: float, max_subdiv: int) -> tuple[int, int]:
    """Compute p and q for a given angle."""
    r = (2 * np.pi - angle) / angle

    p_min, q_min = 0, 0
    _min = np.abs(np.log(r))
    for n in range(4, max_subdiv + 1, 2):
        p, q = np.arange(2, n - 1), np.arange(n - 2, 1, -1)
        v = np.abs(np.log(r * p / q))

        i = v.argmin()
        if v[i] < _min:
            p_min, q_min = p[i], q[i]
            _min = v[i]

        if _min < 1e-12:
            break

    return (int(p_min), int(q_min))


def print_pq(angle: float, pq: tuple[int, int], name: str) -> None:
    p, q = pq
    r = (2 * np.pi - angle) * p / (angle * q)
    r = max(r, 1 / r)
    print(f"{name}: ({p}, {q}) -> {r:.4f}")

    return None


def accumulate_ranges(ranges: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Accumulate overlapping ranges."""
    if not ranges:
        return []

    ranges.sort()
    accumulated = [ranges[0]]

    for current in ranges[1:]:
        last = accumulated[-1]
        if current[0] <= last[1]:
            accumulated[-1] = (last[0], max(last[1], current[1]))
        else:
            accumulated.append(current)

    return accumulated


def plot_angles(N: int, g: float) -> None:
    fig, ax = plt.subplots()

    ax.set_xlim(-0.1, np.pi + 0.1)
    ax.set_xticks(
        ticks=np.pi * np.array([0.0, 0.25, 0.5, 0.75, 1.0]),
        labels=[r"$0$", r"$\pi/4$", r"$\pi/2$", r"$3\pi/4$", r"$\pi$"],
    )
    ax.grid(True, zorder=1)

    ranges = []
    for n in range(2, N + 1, 2):
        p = np.arange(2, n // 2 + 1)
        q = n - p
        _min, _max = ((2 * np.pi) * p / (p + g * q), (g * 2 * np.pi) * p / (g * p + q))
        ranges.extend([(float(a), float(b)) for a, b in zip(_min, _max)])

    for rat in accumulate_ranges(ranges):
        ax.axvspan(rat[0], rat[1], color="C0", alpha=0.25, zorder=2)

    rationals: set[Fraction] = set()
    for n in range(1, N + 1):
        for a in range(1, n + 1):
            rationals.add(Fraction(a, n))

    angles: list[float] = []
    denominators: list[int] = []
    for rat in sorted(rationals):
        angles.append(float(rat * np.pi))
        denominators.append(rat.denominator)

    ax.scatter(angles, denominators, marker="x", color="C1", zorder=3)

    plt.show()

    return None


def main(n: int) -> None:
    angles = np.linspace(0, np.pi, n + 2)[1:-1]
    for angle in angles:
        print(f"Angle = {angle / np.pi:.4f} * pi")
        print_pq(angle, compute_pq_frac(angle, max_denominator=12), "frac")
        print_pq(angle, compute_pq_min(angle, max_subdiv=16), " min")


if __name__ == "__main__":
    main(8)
    plot_angles(16, 1.1)
