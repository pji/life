"""
codec
~~~~~

File I/O codecs for :mod:`life`.
"""
from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from life import util


# Constants.
Y, X = 1, 0


# Base classes.
class Codec(ABC):
    """A base class for codecs."""
    @classmethod
    @abstractmethod
    def decode(cls, text: str) -> NDArray[np.bool_]:
        """Read a serialized array."""

    @classmethod
    @abstractmethod
    def encode(cls, a: NDArray[np.bool_]) -> str:
        """Serialize an array."""


# Classes.
class Cells(Codec):
    @classmethod
    def decode(cls, text: str) -> NDArray[np.bool_]:
        """Read an array that has been serialized in `cells` format."""
        if text.endswith('\n'):
            text = text[:-1]
        lines = text.split('\n')
        lines = [line for line in lines if not line.startswith('!')]
        height = len(lines)
        width = max(len(line) for line in lines)
        normal = [util.normalize_width(line, width) for line in lines]
        return np.array(
            [util.char_to_bool(line, 'O') for line in normal],
            dtype=bool
        )

    @classmethod
    def encode(cls, a: NDArray[np.bool_]) -> str:
        """Write the array as a string in `cells` format."""
        a = remove_padding(a)
        out: NDArray[np.str_] = np.ndarray(a.shape, dtype='<U1')
        out.fill('.')
        out[a] = 'O'
        return '\n'.join(''.join(c for c in row) for row in out) + '\n'


class Pattern(Codec):
    @classmethod
    def decode(cls, text: str) -> NDArray[np.bool_]:
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
    def encode(cls, a: NDArray[np.bool_]) -> str:
        """Write the array as a string in `pattern` format."""
        a = remove_padding(a)
        out: NDArray[np.str_] = np.ndarray(a.shape, dtype='<U1')
        out.fill('.')
        out[a] = 'X'
        return '\n'.join(''.join(c for c in row) for row in out)


# Registration.
codecs = {
    'cells': Cells,
    'pattern': Pattern,
}


# Coding functions.
def decode(text: str, codec: str):
    """Deserialize a string."""
    decoder = codecs[codec]
    return decoder.decode(text)


def encode(a: NDArray[np.bool_], codec: str):
    """Deserialize a string."""
    encoder = codecs[codec]
    return encoder.encode(a)


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
    while not a[:, x_start].any() and x_start < a.shape[X]:
        x_start += 1

    # Find last column with pattern.
    x_end = a.shape[X]
    while not a[:, x_end - 1].any() and x_end > 0:
        x_end -= 1

    # return [row[x_start:x_end] for row in data[y_start:y_end]]
    return a[y_start:y_end, x_start:x_end]
