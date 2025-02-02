"""
test_codec
~~~~~~~~~~

Unit tests for file I/O codecs.
"""
import numpy as np
import pytest as pt

from life import codec, util


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


@pt.fixture
def info():
    """A :class:`util.FileInfo` object for testing."""
    return util.FileInfo('spam', 'egg', 'B3/S23', 'bacon')


class TestCells:
    def test_decode(self, data):
        """When given a string, :meth:`Cells.decode` should return that
        string as an :class:`numpy.ndarray`.
        """
        actual, actual_info = codec.Cells.decode(
            '!Name: spam\n'
            '! bacon\n'
            '.....\n'
            '.OOO.\n'
            '...O.\n'
            '..O..\n'
            '.....'
        )
        assert (actual == data).all()
        assert actual_info == util.FileInfo('spam', comment='bacon')

    def test_encode(self, data, info):
        """When given an array, :meth:`Cells.encode` should return
        that array as a string in `pattern` format.
        """
        assert codec.Cells.encode(data, info) == (
            '!Name: spam\n'
            '! egg\n'
            '! B3/S23\n'
            '! bacon\n'
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
        actual, actual_info = codec.Pattern.decode(
            '.....\n'
            '.XXX.\n'
            '...X.\n'
            '..X..\n'
            '.....'
        )
        assert (actual == data).all()
        assert actual_info == util.FileInfo()

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
    def test_decode(self, data, info):
        """When given a string, :meth:`RLE.decode` should return that
        string as an :class:`numpy.ndarray`.
        """
        actual, actual_info = codec.RLE.decode(
            '#N spam\n'
            '#O egg\n'
            '#C bacon\n'
            'x = 5, y = 5, rule = B3/S23\n'
            '5b$b3o$3bo$2bo!'
        )
        assert (actual == data).all()
        assert actual_info == info

    def test_encode(self, mocker, data, info):
        """When given an array, :meth:`RLE.encode` should return
        that array as a string in `pattern` format.
        """
        assert codec.RLE.encode(data, info) == (
            '#N spam\n'
            '#O egg\n'
            '#C bacon\n'
            'x = 3, y = 3, rule = B3/S23\n'
            '3o$2bo$bo!'
        )
