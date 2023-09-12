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
