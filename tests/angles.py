from lostinmsh.geometry import Angle, elementary_angle


def main() -> None:
    """Main function."""
    N = 12
    for i in range(2 * N + 1):
        a = Angle(i, N)

        str_a = f"{a}".rjust(6)
        print(f"{str_a} -> {elementary_angle(a)}")


if __name__ == "__main__":
    main()
