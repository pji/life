"""
codec
~~~~~

File I/O codecs for :mod:`life`.
"""
import numpy as np
from numpy.typing import NDArray

from life import util


# Constants.
Y, X = 1, 0


# Classes.
class Pattern:
    @classmethod
    def read(cls, text: str) -> NDArray[np.bool_]:
        """Read an array that has been serialized in `pattern` format."""
        if text.endswith('\n'):
            text = text[:-1]
        lines = text.split('\n')
        height = len(lines)
        width = max(len(line) for line in lines)
        normal = [util.normalize_width(line, width) for line in lines]
        return np.array(
            [util.char_to_bool(line, 'X') for line in normal],
            dtype=bool
        )

    @classmethod
    def write(cls, a: NDArray[np.bool_]) -> str:
        """Write the array as a string in `pattern` format."""
        a = remove_padding(a)
        out: NDArray[np.str_] = np.ndarray(a.shape, dtype='<U1')
        out.fill('.')
        out[a] = 'X'
        return '\n'.join(''.join(c for c in row) for row in out) + '\n'


# Utility functions.
def remove_padding(a: NDArray[np.bool_]) -> NDArray[np.bool_]:
    """Remove empty rows and columns surrounding the pattern."""
    # Find the first row with the pattern.
    y_start = 0
    while not a[y_start, :].any() and y_start < a.shape[Y]:
        y_start += 1

    # Find last row with the pattern.
    y_end = a.shape[Y]
    while not a[y_end - 1, :].any() and y_end > 0:
        y_end -= 1

    # Find first column with the pattern.
    x_start = 0
    while not a[x_start].any() and x_start < a.shape[X]:
        x_start += 1

    # Find last column with pattern.
    x_end = a.shape[X]
    while not a[:, x_end - 1].any() and x_end > 0:
        x_end -= 1

    # return [row[x_start:x_end] for row in data[y_start:y_end]]
    return a[y_start:y_end, x_start:x_end]
