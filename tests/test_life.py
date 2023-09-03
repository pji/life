"""
test_life
~~~~~~~~~

Unit tests for :mod:`life.life`.
"""
import numpy as np
import pytest as pt

from life import life


# Utility functions.
def raises(cls, *args, **kwargs):
    """Return the exception raised by the callable."""
    try:
        cls(*args, **kwargs)
    except Exception as ex:
        return type(ex), str(ex)
    return None


def pat_to_grid(pat):
    width = len(pat[0])
    height = len(pat)
    grid = life.Grid(width, height)
    grid._data = np.array(
        [[True if c == 'X' else False for c in row] for row in pat],
        dtype=bool
    )
    return grid


# Fixtures for Grid.
@pt.fixture
def grid():
    grid = life.Grid(4, 3)
    grid._data[0, 1] = True
    grid._data[0, 3] = True
    grid._data[2, 1] = True
    return grid


# Tests for Grid class methods.
def test_from_array():
    """Given a :class:`numpy.ndarray`, :meth:`Grid.from_array` should
    return a new instance of :class:`Grid` using that array.
    """
    grid = life.Grid.from_array(np.array([
        [0, 1],
        [1, 0],
    ], dtype=bool), 'B3/S23')
    assert (grid._data == np.array([
        [0, 1],
        [1, 0],
    ], dtype=bool)).all()
    assert grid.rule == 'B3/S23'


# Tests for Grid initialization.
def test_init_all_default():
    """Given only required parameters, :class:`Grid` should set the
    required attributes to the given values and the optional attributes
    to the default values.
    """
    required = {
        'height': 3,
        'width': 2,
    }
    optional = {
        'rule': 'B3/S23'
    }
    grid = life.Grid(**required)
    for attr in required:
        assert getattr(grid, attr) == required[attr]
    for attr in optional:
        assert getattr(grid, attr) == optional[attr]


def test_init_all_optional():
    """Given only all parameters, :class:`Grid` should set the
    given attributes to the given values.
    """
    required = {
        'height': 3,
        'width': 2,
    }
    optional = {
        'rule': 'B4/S234'
    }
    grid = life.Grid(**required, **optional)
    for attr in required:
        assert getattr(grid, attr) == required[attr]
    for attr in optional:
        assert getattr(grid, attr) == optional[attr]


def test_init_creates_empty_grid():
    """Initializing a :class:`Grid` generates an empty Game of
    Life grid.
    """
    grid = life.Grid(4, 3)
    assert (grid._data == np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ], dtype=bool)).all()


# Tests for Grid representations.
def test_comparisons(grid):
    """Two :class:`Grid` objects with the same array and rules should
    compare as equal.
    """
    equal = life.Grid.from_array(grid._data, grid.rule)
    different = life.Grid(5, 5)
    assert grid == equal
    assert grid is not equal
    assert grid != different


def test_repr(grid):
    """:class:`Grid` objects should be able to produce a simple
    string representation of themselves for debugging.
    """
    assert repr(grid) == "Grid(4, 3, 'B3/S23')"


def test_str(grid):
    """:class:`Grid` objects should be able to produce a simple
    string representation of themselves.
    """
    assert str(grid) == (
        '.X.X\n'
        '....\n'
        '.X..'
    )


# Tests for protocols.
def test_sequence_protocol(grid):
    """:class:`Grid` should implement the :class:`Sequence` protocol."""
    assert len(grid) == 3
    assert True in grid
    assert grid.index(True) == (0, 1)
    assert grid.count(True) == 3
    assert (grid[0] == np.array(grid._data[0])).any()
    assert grid[0][1]
    assert grid[0, 1]

#     rev_iter = reversed(grid)
#     assert not next(rev_iter)
#     assert not next(rev_iter)
#     assert next(rev_iter)

    grid._data = np.array([
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 0],
    ], dtype=bool)
    giter = iter(grid)
    assert (next(giter) == np.array([
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 1, 1],
        [0, 1, 0, 1],
    ], dtype=bool)).all()


def test_mutablesequence_protocol(grid):
    """:class:`Grid` should implement the :class:`MutableSequence`
    protocol.
    """
    # We are only implementing __setitem__.
    grid[0][0] = True
    grid[0, 2] = True
    assert (grid._data == np.array([
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 1, 0, 0],
    ], dtype=bool)).all()

    # It doesn't make sense to fully implement MutableSequence.
    assert raises(grid.__delitem__, 0) == tuple([
        life.PartialImplentation,
        'Locations in a Grid cannot be deleted.',
    ])
    assert raises(grid.insert, 0, []) == tuple([
        life.PartialImplentation,
        'Locations cannot be inserted into a Grid.',
    ])
    assert raises(grid.pop, 0) == tuple([
        life.PartialImplentation,
        'Locations cannot be popped from a Grid.',
    ])
    assert raises(grid.remove, 0) == tuple([
        life.PartialImplentation,
        'Locations cannot be removed from a Grid.',
    ])
    assert raises(grid.__iadd__, 0) == tuple([
        life.PartialImplentation,
        'Locations cannot be added incrementally to a Grid.',
    ])


# Tests for properties.
def test_array_properties(grid):
    """Some properties of the data array should be available
    as properties.
    """
    assert grid.shape == (3, 4)


def test_rule_properties(grid):
    """The definitions of the rules for the game should be available
    as properties.
    """
    assert grid.rule == 'B3/S23'
    assert grid.born == (3,)
    assert grid.survive == (2, 3)


# Tests for running the game.
def test_clear(grid):
    """When called, :meth:`Grid.clear` should clear all values
    from the grid.
    """
    grid.clear()
    assert (grid._data == np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ], dtype=bool)).all()


def test_flip(grid):
    """When called with X and Y coordinates, :meth:`Grid.flip` should
    change the value of that location on the :class:`Grid` to the
    opposite value.
    """
    assert not grid._data[1][2]
    grid.flip(2, 1)
    assert grid._data[1][2]
    grid.flip(2, 1)
    assert not grid._data[1][2]


def test_randomize(grid):
    """When called, :meth:`Grid.randomize` should randomize the
    values in the :class:`Grid`.
    """
    grid.rng = np.random.default_rng(seed=1138)
    grid.randomize()
    assert (grid._data == np.array([
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [0, 1, 1, 0],
    ], dtype=bool)).all()


def test_replace_larger(grid):
    """Given a two-dimensional :class:`Sequence` of :class:`bool`-like
    values, :meth:`Grid.replace` should resize the existing :class:`Grid`
    to the size of the given :class:`Sequence` and set the values of
    the :class:`Grid` to the given values.
    """
    grid.replace([
        [0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0],
    ])
    assert (grid._data == np.array([
        [0, 1, 0, 1],
        [0, 1, 0, 1],
        [0, 1, 0, 1],
    ], dtype=bool)).all()


def test_replace_smaller(grid):
    """Given a two-dimensional :class:`Sequence` of :class:`bool`-like
    values, :meth:`Grid.replace` should resize the existing :class:`Grid`
    to the size of the given :class:`Sequence` and set the values of
    the :class:`Grid` to the given values.
    """
    grid.replace([
        [0, 1],
        [1, 0],
    ])
    assert (grid._data == np.array([
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 0],
    ], dtype=bool)).all()


def test_tick(grid):
    """When called, :meth:`Grid.tick` should advance the game
    one generation.
    """
    grid.tick()
    assert (grid._data == np.array([
        [1, 0, 1, 0],
        [1, 0, 1, 0],
        [1, 0, 1, 0],
    ], dtype=bool)).all()

    grid._data = np.array([
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 0],
    ], dtype=bool)
    grid.tick()
    assert (grid._data == np.array([
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 1, 1],
        [0, 1, 0, 1],
    ], dtype=bool)).all()

    grid = pat_to_grid([
        '........X.......',
        '.......X..X.....',
        '........XXXX....',
        '........XXXXX...',
        '....X..X..XX....',
        '...X.XX...XX.X..',
        '.....XX..X..X...',
        '....XXXXX.......',
        '.....XXXX.......',
        '......X..X......',
        '........X.......',
        '................',
        '................',
        '................',
        '................',
        '................',
    ])
    grid.rule = 'B36/S23'
    grid.tick()
    assert (grid._data == pat_to_grid([
        '................',
        '.......X..XX....',
        '.......X....X...',
        '.......X....X...',
        '....XXXXX.......',
        '.......X.X......',
        '........XXXXX...',
        '....X....X......',
        '....X....X......',
        '.....XX..X......',
        '................',
        '................',
        '................',
        '................',
        '................',
        '................',
    ])._data).all()
