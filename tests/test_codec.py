"""
test_codec
~~~~~~~~~~

Unit tests for file I/O codecs.
"""
import numpy as np
import pytest as pt

from life import codec


# Common fixtures.
@pt.fixture
def data():
    """An array used for testing."""
    return np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ], dtype=bool)


class TestCells:
    def test_decode(self, data):
        """When given a string, :meth:`Cells.decode` should return that
        string as an :class:`numpy.ndarray`.
        """
        assert (codec.Cells.decode(
            '.....\n'
            '.OOO.\n'
            '...O.\n'
            '..O..\n'
            '.....'
        ) == data).all()

    def test_encode(self, data):
        """When given an array, :meth:`Cells.encode` should return
        that array as a string in `pattern` format.
        """
        assert codec.Cells.encode(data) == (
            'OOO\n'
            '..O\n'
            '.O.\n'
        )

        a = np.zeros((84, 80), dtype=bool)
        a[41, 40] = True
        a[42, 39] = True
        a[42, 41] = True
        a[43, 40] = True
        assert codec.Cells.encode(a) == (
            '.O.\n'
            'O.O\n'
            '.O.\n'
        )


class TestPattern:
    def test_decode(self, data):
        """When given a string, :meth:`Pattern.decode` should return that
        string as an :class:`numpy.ndarray`.
        """
        assert (codec.Pattern.decode(
            '.....\n'
            '.XXX.\n'
            '...X.\n'
            '..X..\n'
            '.....'
        ) == data).all()

    def test_encode(self, data):
        """When given an array, :meth:`Pattern.encode` should return
        that array as a string in `pattern` format.
        """
        assert codec.Pattern.encode(data) == (
            'XXX\n'
            '..X\n'
            '.X.'
        )


class TestRLE:
    def test_decode(self, data):
        """When given a string, :meth:`RLE.decode` should return that
        string as an :class:`numpy.ndarray`.
        """
        assert (codec.RLE.decode(
            'x = 5, y = 5\n'
            '5b$b3o$3bo$2bo!'
        ) == data).all()

    def test_encode(self, data):
        """When given an array, :meth:`RLE.encode` should return
        that array as a string in `pattern` format.
        """
        assert codec.RLE.encode(data) == (
            'x = 3, y = 3\n'
            '3o$2bo$bo!'
        )
