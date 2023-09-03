"""
test_util
~~~~~~~~~

Unit tests for :mod:`life.util`.
"""
import numpy as np

from life import util


def test_fit_array():
    """Given an array and a shape for an array, :func:`util.fit_array`
    should slice and pad the array to fit the new shape without changing
    the relative locations of any of the data within the remaining part
    of the array.
    """
    a = np.array([
        [0x00, 0x01, 0x02, 0x03],
        [0x04, 0x05, 0x06, 0x07],
        [0x08, 0x09, 0x0a, 0x0b],
        [0x0c, 0x0d, 0x0e, 0x0f],
    ])
    assert (util.fit_array(a, (3, 5), 0) == np.array([
        [0x00, 0x01, 0x02, 0x03, 0x00],
        [0x04, 0x05, 0x06, 0x07, 0x00],
        [0x08, 0x09, 0x0a, 0x0b, 0x00],
    ])).all()


def test_max_per_index():
    """Given multiple sequences of comparable items,
    :func:`util.max_per_index` should return a :class:`tuple`
    containing the largest value at each index.
    """
    s1 = [1, 6, 7]
    s2 = [2, 5, 8]
    s3 = [3, 4, 9]
    assert util.max_per_index(s1, s2, s3) == (3, 6, 9)


def test_pad_array():
    """Given an array, a new shape for that array that is equal to
    or greater than the current size of the array in every dimension
    and a padding value, :meth:`util.pad_array` should pad the size
    of the given array.
    """
    a = np.array([
        [1, 0],
        [0, 1],
    ], dtype=bool)
    assert (util.pad_array(a, (4, 5), 0) == np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ], dtype=bool)).all()
