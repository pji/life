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

from life.model import LifeAry


Y, X = 0, 1


# Functions.
def char_to_bool(line: str, true: str = 'X') -> list[bool]:
    """Convert the characters in a string to booleans.

    :param line: The line of text to convert.
    :param true: (Optional.) The character that translates as true.
        This is case insensitive. All other characters will translate
        as false. Defaults to `X`.
    :returns: A :class:`list` object.
    :rtype: list
    """
    result: list[bool] = []
    for char in line:
        if char.casefold() == true.casefold():
            result.append(True)
        else:
            result.append(False)
    return result


def fit_array(a: LifeAry, shape: tuple[int, ...], fill: Any = 0) -> LifeAry:
    """Fit the given array into the given shape.

    :param a: The array to fit.
    :param shape: The shape to fit the array into.
    :param fill: The value to use when filling any new area.
    :returns: A :class:`life.model.LifeAry` object.
    :rtype: life.model.LifeAry

    Usage::

        >>> import numpy as np
        >>>
        >>> # A base array to alter.
        >>> a = np.array([
        ...     [False, False, False, False, False],
        ...     [False, True, True, True, False],
        ...     [False, False, False, True, False],
        ...     [False, False, True, False, False],
        ...     [False, False, False, False, False],
        ... ])
        >>>
        >>> # Shrink the 5x5 array into a 3x3 array.
        >>> a = fit_array(a, (3, 3))
        >>> a
        array([[ True,  True,  True],
               [False, False,  True],
               [False,  True, False]])
        >>>
        >>> # Expand the 3x3 array into a 7x7 array, filling the
        >>> # new area with True.
        >>> a = fit_array(a, (7, 7), fill=True)
        >>> a
        array([[ True,  True,  True,  True,  True,  True,  True],
               [ True,  True,  True,  True,  True,  True,  True],
               [ True,  True,  True,  True,  True,  True,  True],
               [ True,  True, False, False,  True,  True,  True],
               [ True,  True, False,  True, False,  True,  True],
               [ True,  True,  True,  True,  True,  True,  True],
               [ True,  True,  True,  True,  True,  True,  True]])
    """
    max_shape = max_per_index(a.shape, shape)
    padded = pad_array(a, max_shape, fill)
    diffs = (m - n for m, n in zip(max_shape, shape))
    slices = [
        slice(n // 2, m - (n - (n // 2)))
        for n, m in zip(diffs, max_shape)
    ]
    return padded[slices[Y], slices[X]]


def pad_array(a: LifeAry, new_shape: Sequence[int], fill: Any) -> LifeAry:
    """Resize the given array to the given new shape.

    :param a: The array to pad.
    :param new_shape: The shape to pad the array into.
    :param fill: The value to use when filling any new area.
    :returns: A :class:`life.model.LifeAry` object.
    :rtype: life.model.LifeAry

    Usage::

        >>> import numpy as np
        >>>
        >>> # A base array to alter.
        >>> a = np.array([
        ...     [False, False, False, False, False],
        ...     [False, True, True, True, False],
        ...     [False, False, False, True, False],
        ...     [False, False, True, False, False],
        ...     [False, False, False, False, False],
        ... ])
        >>>
        >>> a = pad_array(a, (7, 7), fill=True)
        >>> a
        array([[ True,  True,  True,  True,  True,  True,  True],
               [ True, False, False, False, False, False,  True],
               [ True, False,  True,  True,  True, False,  True],
               [ True, False, False, False,  True, False,  True],
               [ True, False, False,  True, False, False,  True],
               [ True, False, False, False, False, False,  True],
               [ True,  True,  True,  True,  True,  True,  True]])
    """
    diffs = [n - o for n, o in zip(new_shape, a.shape)]
    pads = [(n // 2, n - (n // 2)) for n in diffs]
    return np.pad(a, pads, constant_values=fill)


def max_per_index(*seqs: Sequence[int]) -> tuple[int, ...]:
    """Return the maximum value for each index.

    :param seqs: The sequences to compare. They should be passed in
        as individual sequences. See the usage example below.
    :returns: A :class:`tuple` object.
    :rtype: tuple

    Usage::

        >>> shape_a = (7, 6)
        >>> shape_b = (5, 8)
        >>> result = max_per_index(shape_a, shape_b)
        >>> result
        (7, 8)
    """
    result = [max(group) for group in zip_longest(*seqs)]
    return tuple(result)


def normalize_width(line: str, width: int, fill: str = '.') -> str:
    """Extend line to match the list.

    :param line: The line to extend.
    :param width: The width to extend the line to.
    :param fill: (Optional.) The character to use when extending the line.
    :returns: A :class:`str` object.
    :rtype: str

    Usage::

        >>> line = 'x.x.xx'
        >>> result = normalize_width(line, 10, fill='x')
        >>> result
        'x.x.xxxxxx'
    """
    if len(line) < width:
        line += fill * (width - len(line))
    return line


# Classes.
@dataclass
class FileInfo:
    """Metadata for saved files.

    :param name: The name of the file.
    :param user: The creator of the file.
    :param rule: The rules for the Game of Life.
    :param comment: A comment describing the file.
    :returns: A :class:`life.util.FileInfo` object.
    :rtype: life.util.FileInfo

    Usage::

        >>> name = 'spam.pattern'
        >>> user = 'Graham Chapman'
        >>> rule = 'b3/s23'
        >>> comment = 'A spammy pattern.'
        >>> fileinfo = FileInfo(name, user, rule, comment)
    """
    name: str = ''
    user: str = ''
    rule: str = ''
    comment: str = ''
