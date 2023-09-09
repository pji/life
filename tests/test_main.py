"""
test_main
~~~~~~~~~

Unit tests for :mod:`life.__main__`.
"""
from life import sui
from life.main import main


# Tests for main.
def test_main_simple_loop(mocker):
    """The :funct:`main` loop should start and end a game of life."""
    mocker.patch('sys.argv', ['life',])
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    main()


def test_main_f(mocker):
    """When invoked from the command line with `-f` followed by a
    the path to a valid pattern file, :func:`main` should create a
    :class:`Start` object with :attr:`Start.file` set to the given
    path.
    """
    start = sui.Start()
    mock_start = mocker.patch('life.main.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-f tests/data/spam'])
    main()
    assert mock_start.call_args[1]['file'] == 'tests/data/spam'


def test_main_p(mocker):
    """When invoked from the command line with `-p` followed by a
    a floating point number, :func:`main` should create a
    :class:`Start` object with :attr:`Start.pace` set to the given
    number.
    """
    start = sui.Start()
    mock_start = mocker.patch('life.main.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-p 0.01'])
    main()
    assert mock_start.call_args[1]['pace'] == 0.01


def test_main_r(mocker):
    """When invoked from the command line with `-r` followed by a
    valid rule string, :func:`main` should create a :class:`Start`
    object with :attr:`Start.rule` set to the given rule string.
    """
    start = sui.Start()
    mock_start = mocker.patch('life.main.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-r B36/S23'])
    main()
    assert mock_start.call_args[1]['rule'] == 'B36/S23'


def test_main_W(mocker):
    """When invoked from the command line with `-W`, :func:`main`
    should create a :class:`Start` object with :attr:`Start.wrap`
    set to `False`.
    """
    start = sui.Start()
    mock_start = mocker.patch('life.main.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-W'])
    main()
    assert mock_start.call_args[1]['wrap'] is False
