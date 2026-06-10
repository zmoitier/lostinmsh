"""Helper functions for circular iteration."""

from collections.abc import Collection
from itertools import cycle, islice
from typing import Iterable


def circular[T](collection: Collection[T], start: int = 0) -> Iterable[T]:
    """Return the circular iterator from a collection.

    Parameters
    ----------
    collection : Collection[T]
        sequence-like object with a length
    start : int, optional
        starting index, by default 0

    Returns
    -------
    Iterable[T]
        circular iterator
    """
    end = start + len(collection)
    return islice(cycle(collection), start, end)


def circular_pairwise[T](
    collection: Collection[T], start: int = 0
) -> Iterable[tuple[T, T]]:
    """Return the circular pair-wise iterator from a collection.

    Parameters
    ----------
    collection : Collection[T]
        sequence-like object with a length
    start : int, optional
        starting index, by default 0

    Returns
    -------
    Iterable[tuple[T, T]]
        circular pair-wise iterator
    """
    end = start + len(collection)
    return zip(
        islice(cycle(collection), start, end),
        islice(cycle(collection), start + 1, None),
    )


def circular_triplewise[T](
    collection: Collection[T], start: int = 0
) -> Iterable[tuple[T, T, T]]:
    """Return the circular triple-wise iterator from a collection.

    Parameters
    ----------
    collection : Collection[T]
        sequence-like object with a length
    start : int, optional
        starting index, by default 0

    Returns
    -------
    Iterable[tuple[T, T, T]]
        circular triple-wise iterator
    """
    end = start + len(collection)
    return zip(
        islice(cycle(collection), start, end),
        islice(cycle(collection), start + 1, None),
        islice(cycle(collection), start + 2, None),
    )
