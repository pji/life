"""
test_main
~~~~~~~~~

Unit tests for :mod:`life.__main__`.
"""
import blessed
import numpy as np
import pytest as pt

from life import life, sui
from life.main import main


# Common fixtures.
@pt.fixture
def data_start():
    return np.array([
        [0, 1, 0, 1],
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
    ], dtype=bool)


@pt.fixture
def grid(data_start):
    """A :class:`Grid` object for testing."""
    grid = life.Grid(4, 4)
    grid._data = data_start
    return grid


@pt.fixture
def term(mocker):
    """A :class:`blessed.Terminal` object for testing."""
    mocker.patch('blessed.Terminal.inkey')
    mocker.patch(
        'blessed.Terminal.height',
        return_value=5,
        new_callable=mocker.PropertyMock
    )
    mocker.patch(
        'blessed.Terminal.width',
        return_value=4,
        new_callable=mocker.PropertyMock
    )
    return blessed.Terminal()


# Tests for main.
def test_main_simple_loop(mocker):
    """The :funct:`main` loop should start and end a game of life."""
    mocker.patch('sys.argv', ['life',])
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    main()


def test_main_d(mocker, grid, term):
    """When invoked from the command line with `-d` followed by a
    two integers, :func:`main` should create a :class:`Start` object
    with :attr:`Start.data.height` and `Start.data.width` set to the
    given integers.
    """
    start = sui.Start(grid, term)
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-d', '200', '200',])
    main()
    grid = mock_start.call_args[1]['data']
    assert grid.height == 200
    assert grid.width == 200


def test_main_f(mocker, grid, term):
    """When invoked from the command line with `-f` followed by a
    the path to a valid pattern file, :func:`main` should create a
    :class:`Start` object with :attr:`Start.file` set to the given
    path.
    """
    start = sui.Start(grid, term)
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mock_load = mocker.patch('life.sui.Load.load')
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-f tests/data/spam'])
    main()
    assert mock_load.call_args[0] == ('tests/data/spam',)


def test_main_g(mocker, grid, term):
    """When invoked from the command line with
    `-g`, :func:`main` should create a :class:`Start`
    object with :attr:`Start.show_generation` set to
    `True`.
    """
    start = sui.Start(grid, term)
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-g',])
    main()
    assert mock_start.call_args[1]['show_generation'] is True


def test_main_p(mocker, grid, term):
    """When invoked from the command line with `-p` followed by a
    a floating point number, :func:`main` should create a
    :class:`Start` object with :attr:`Start.pace` set to the given
    number.
    """
    start = sui.Start(grid, term)
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-p 0.01'])
    main()
    assert mock_start.call_args[1]['pace'] == 0.01


def test_main_r(mocker, grid, term):
    """When invoked from the command line with `-r` followed by a
    valid rule string, :func:`main` should create a :class:`Start`
    object with :attr:`Start.rule` set to the given rule string.
    """
    start = sui.Start(grid, term)
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-r B36/S23'])
    main()
    assert mock_start.call_args[1]['data'].rule == 'B36/S23'


def test_main_W(mocker, grid, term):
    """When invoked from the command line with `-W`, :func:`main`
    should create a :class:`Start` object with :attr:`Start.wrap`
    set to `False`.
    """
    start = sui.Start(grid, term)
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-W'])
    main()
    assert mock_start.call_args[1]['data'].wrap is False
