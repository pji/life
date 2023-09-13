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
Y, X = 0, 1


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


class RLE(Codec):
    @classmethod
    def decode(cls, text: str) -> NDArray[np.bool_]:
        """Read an array that has been serialized in `RLE` format."""
        def get_shape(line: str) -> tuple[int, int]:
            parts = line.split(',')
            data = {}
            for part in parts:
                key, value = part.split('=')
                data[key.strip()] = value.strip()
            return int(data['y']), int(data['x'])

        def get_rows(lines: list[str]) -> list[str]:
            joined = ''.join(lines)
            return joined.split('$')

        def get_live_slices(rows: list[str]) -> list[tuple[int, slice]]:
            result = []
            for y, row in enumerate(rows):
                tokens: list[str] = []
                buffer = ''
                for c in row:
                    if c.isdigit():
                        buffer += c
                    elif buffer:
                        tokens.append(buffer)
                        buffer = ''
                        tokens.append(c)
                    else:
                        tokens.append(c)

                # raise ValueError(tokens)
                start = 0
                stop = 1
                for token in tokens:
                    if token.isnumeric():
                        stop = start + int(token)
                    elif token == 'o':
                        result.append((y, slice(start, stop)))
                        start = stop
                        stop = start + 1
                    else:
                        start = stop
                        stop = start + 1

            return result

        if text.endswith('\n'):
            text = text[:-1]
        text = text.split('!')[0]
        lines = text.split('\n')
        lines = [line for line in lines if not line.startswith('#')]

        shape = get_shape(lines[0])
        rows = get_rows(lines[1:])

        a = np.zeros(shape, dtype=bool)
        for y, x in get_live_slices(rows):
            a[y, x] = True
        return a

    @classmethod
    def encode(cls, a: NDArray[np.bool_]) -> str:
        """Write the array as a string in `cells` format."""
        def compress_row(row: str) -> str:
            result = ''
            count = 0
            state: str = ''
            for c in row:
                if state != c:
                    if count > 0:
                        result += str(count + 1)
                    result += state
                    count = 0
                    state = c
                else:
                    count += 1
            else:
                if count > 0:
                    result += str(count + 1)
                result += c
            while 'o' in result and not result.endswith('o'):
                result = result[:-1]
            return result

        a = remove_padding(a)

        result = ''
        result += f'x = {a.shape[X]}, y = {a.shape[Y]}\n'

        out: NDArray[np.str_] = np.ndarray(a.shape, dtype='<U1')
        out.fill('b')
        out[a] = 'o'
        rows = [''.join(c for c in row) for row in out]
        result += '$'.join(compress_row(row) for row in rows) + '!'
        return result


# Registration.
codecs = {
    'cells': Cells,
    'pattern': Pattern,
    'rle': RLE,
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

    # Return the unpadded data.
    return a[y_start:y_end, x_start:x_end]
