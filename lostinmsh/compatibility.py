import sys

if sys.version_info < (3, 12):
    from itertools import islice
    from typing import Iterable, TypeVar

    T = TypeVar("T")

    def batched(iterable: Iterable[T], n: int) -> Iterable[tuple[T, ...]]:
        if n < 1:
            raise ValueError("n must be at least one")
        iterator = iter(iterable)
        while batch := tuple(islice(iterator, n)):
            yield batch
else:
    from itertools import batched
