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


class TestPattern:
    def test_read(self, data):
        """When given a string, :meth:`Pattern.read` should return that
        string as an :class:`numpy.ndarray`.
        """
        assert (codec.Pattern.read(
            '.....\n'
            '.XXX.\n'
            '...X.\n'
            '..X..\n'
            '.....'
        ) == data).all()

    def test_write(self, data):
        """When given an array, :meth:`Pattern.write` should return
        that array as a string in `pattern` format.
        """
        assert codec.Pattern.write(data) == (
            'XXX\n'
            '..X\n'
            '.X.\n'
        )
