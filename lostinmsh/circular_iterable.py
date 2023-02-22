"""Helper functions for circular iteration."""


from collections.abc import Collection
from itertools import cycle, islice
from typing import Iterable


def circular_pairwise(collection: Collection, start: int = 0) -> Iterable:
    """Circular pairwise."""
    end = start + len(collection)
    return zip(
        islice(cycle(collection), start, end),
        islice(cycle(collection), start + 1, None),
    )


def circular_triplewise(collection: Collection, start: int = 0) -> Iterable:
    """Circular triplewise."""
    end = start + len(collection)
    return zip(
        islice(cycle(collection), start, end),
        islice(cycle(collection), start + 1, None),
        islice(cycle(collection), start + 2, None),
    )
