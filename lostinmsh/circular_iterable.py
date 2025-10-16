"""Helper functions for circular iteration."""

from collections.abc import Collection
from itertools import cycle, islice
from typing import Iterable, TypeVar

T = TypeVar("T")


def circular_pairwise(
    collection: Collection[T], start: int = 0
) -> Iterable[tuple[T, T]]:
    """Return the circular pairwise iterator from a collection.

    Parameters
    ----------
    collection : Collection
        sequence-like object with a length
    start : int, optional
        starting index, by default 0

    Returns
    -------
    Iterable
        circular pairwise iterator
    """
    end = start + len(collection)
    return zip(
        islice(cycle(collection), start, end),
        islice(cycle(collection), start + 1, None),
    )


def circular_triplewise(
    collection: Collection[T], start: int = 0
) -> Iterable[tuple[T, T, T]]:
    """Return the circular triplewise iterator from a collection.

    Parameters
    ----------
    collection : Collection
        sequence-like object with a length
    start : int, optional
        starting index, by default 0

    Returns
    -------
    Iterable
        circular triplewise iterator
    """
    end = start + len(collection)
    return zip(
        islice(cycle(collection), start, end),
        islice(cycle(collection), start + 1, None),
        islice(cycle(collection), start + 2, None),
    )
