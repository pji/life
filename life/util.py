"""
util
~~~~

Utility functions for :mod:`life`.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import zip_longest
from typing import Any, Iterator

import numpy as np


Y, X = 0, 1


# Functions.
def char_to_bool(line: str, true: str = 'X') -> list[bool]:
    """Convert the characters in a string to booleans."""
    result: list[bool] = []
    for char in line:
        if char.casefold() == true.casefold():
            result.append(True)
        else:
            result.append(False)
    return result


def fit_array(
    a: np.ndarray, shape: tuple[int, ...], fill: Any = 0
) -> np.ndarray:
    """Fit the given array into the given shape."""
    max_shape = max_per_index(a.shape, shape)
    padded = pad_array(a, max_shape, fill)
    diffs = (m - n for m, n in zip(max_shape, shape))
    slices = [
        slice(n // 2, m - (n - (n // 2))) for n, m in zip(diffs, max_shape)
    ]
    return padded[slices[Y], slices[X]]


def pad_array(
    a: np.ndarray, new_shape: Sequence[int], fill: Any
) -> np.ndarray:
    """Resize the given array to the given new shape."""
    diffs = [n - o for n, o in zip(new_shape, a.shape)]
    pads = [(n // 2, n - (n // 2)) for n in diffs]
    return np.pad(a, pads, constant_values=fill)


def max_per_index(*seqs: Sequence[int]) -> tuple[int, ...]:
    """Return the maximum value for each index."""
    result = [max(group) for group in zip_longest(*seqs)]
    return tuple(result)


def normalize_width(line: str, width: int, fill: str = '.') -> str:
    """Extend line to match the list."""
    if len(line) < width:
        line += fill * (width - len(line))
    return line


# Classes.
@dataclass
class FileInfo:
    """Metadata for saved files."""
    name: str = ''
    user: str = ''
    rule: str = ''
    comment: str = ''
