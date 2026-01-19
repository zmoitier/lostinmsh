from fractions import Fraction

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


def main(n: int) -> None:
    angles = np.linspace(0, np.pi, n + 2)[1:-1]
    for angle in angles:
        print(f"Angle = {angle}")
        print_pq(angle, compute_pq_frac(angle, max_denominator=12), "frac")
        print_pq(angle, compute_pq_min(angle, max_subdiv=16), " min")


if __name__ == "__main__":
    main(13)
