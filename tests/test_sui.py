"""
test_sui
~~~~~~~

This provides the unit tests for life.sui.py.
"""
from pathlib import Path

import blessed
import numpy as np
import pytest as pt

from life import life, sui


# Terminal keys:
DOWN = '\x1b[B'
UP = '\x1b[A'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'

# Common arrays.
data_next = np.array([
    [1, 0, 1, 0],
    [1, 0, 1, 0],
    [0, 0, 0, 0],
    [0, 1, 0, 0],
], dtype=bool)

# Common lines.
term_ = blessed.Terminal()
grid_start_lines = (
    term_.move(0, 0) + ' \u2580 \u2580\n'
    + term_.move(1, 0) + ' \u2588  \n'
)
grid_next_lines = (
    term_.move(0, 0) + '\u2588 \u2588 \n'
    + term_.move(1, 0) + ' \u2584  \n'
)


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
def big_grid():
    """A 6x6 :class:`life.Grid` object for testing."""
    grid = life.Grid(6, 6)
    grid._data = np.array([
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
    ], dtype=bool)
    return grid


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


@pt.fixture
def small_term(mocker):
    """A 2x4 :class:`bless.Terminal` object for testing."""
    mocker.patch('blessed.Terminal.inkey')
    mocker.patch(
        'blessed.Terminal.height',
        return_value=4,
        new_callable=mocker.PropertyMock
    )
    mocker.patch(
        'blessed.Terminal.width',
        return_value=2,
        new_callable=mocker.PropertyMock
    )
    term = blessed.Terminal()
    return term


# Fixtures for Autorun.
@pt.fixture
def autorun(grid, term):
    return sui.Autorun(grid, term)


@pt.fixture
def window_autorun(big_grid, small_term):
    autorun = sui.Autorun(big_grid, small_term)
    autorun.origin_x = 1
    autorun.origin_y = 3
    return autorun


# Tests for Autorun initialization.
def test_Autorun_init(grid, term):
    """When given required parameters, :class:`Autorun` should return
    an instance with attributes set to the given values.
    """
    required = {
        'data': grid,
        'term': term,
    }
    obj = sui.Autorun(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]


# Tests for Autorun input.
def test_Autorun_input_keypress(autorun):
    """If a key is pressed, :meth:`Autorun.input` should return an
    exit command string.
    """
    autorun.term.inkey.return_value = ' '
    assert autorun.input() == ('exit',)


def test_Autorun_input_timeout(autorun):
    """If no key is pressed, :meth:`Autorun.input` should return a
    run command string.
    """
    autorun.term.inkey.return_value = ''
    assert autorun.input() == ('run',)


# Tests for Autorun commands.
def test_Autorun_exit(autorun):
    """When called :func:`Autorun.exit` should return a :class:`Core`
    object populated with its :class:`Grid` and :class:`blessed.Terminal`
    objects.
    """
    state = autorun.exit()
    assert isinstance(state, sui.Core)
    assert state.data is autorun.data
    assert state.term is autorun.term


def test_Autorun_exit(window_autorun):
    """When called :func:`Autorun.exit` should return a :class:`Core`
    object populated with its :class:`Grid` and :class:`blessed.Terminal`
    objects.
    """
    state = window_autorun.exit()
    assert isinstance(state, sui.Core)
    assert state.data is window_autorun.data
    assert state.term is window_autorun.term
    assert state.origin_x == window_autorun.origin_x
    assert state.origin_y == window_autorun.origin_y


def test_Autorun_run(autorun):
    """When called, :meth:`Autorun.run` should advance the grid and
    return the :class:`Autorun` object.
    """
    state = autorun.run()
    assert state is autorun
    assert (autorun.data._data == data_next).all()


# Tests for Autorun UI updates.
def test_Autorun_update_ui(capsys, autorun, term):
    """When called, :meth:`Autorun.update_ui` should redraw the UI."""
    autorun.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        grid_start_lines
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + autorun.menu + term.clear_eol
    )


# Fixtures for Config.
@pt.fixture
def config(grid, term):
    """A :class:`Config` object for testing."""
    config = sui.Config(grid, term)
    return config


# Tests for Config initialization.
def test_Config_init_all_defaults(grid, term):
    """When given required parameters, :class:`Config` should return
    an instance with attributes set to the default values.
    """
    required = {
        'data': grid,
        'term': term,
    }
    optional = {
        'origin_x': 0,
        'origin_y': 0,
    }
    obj = sui.Config(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]
    for attr in optional:
        assert getattr(obj, attr) is optional[attr]


def test_Config_init_all_optional(grid, term):
    """When given optional parameters, :class:`Config` should return
    an instance with attributes set to the given values.
    """
    optional = {
        'data': grid,
        'term': term,
        'origin_x': 2,
        'origin_y': 1,
    }
    obj = sui.Config(**optional)
    for attr in optional:
        assert getattr(obj, attr) is optional[attr]


# Tests for Config commands.
def test_Config_down(config):
    """When called, :meth:`Config.down` should increment
    :attr:`Config.selected` and return itself.
    """
    state = config.down()
    assert state is config
    assert config.selected == 1


def test_Config_down_wrap(config):
    """When called, :meth:`Config.down` should increment
    :attr:`Config.selected` and return itself. If down is
    called when the last setting is selected, select the
    first setting.
    """
    config.selected = 1
    state = config.down()
    assert state is config
    assert config.selected == 0


def test_Config_exit(config):
    """When called, :meth:`Config.exit` should return a
    :class:`Core` object.
    """
    state = config.exit()
    assert isinstance(state, sui.Core)
    assert state.data is config.data
    assert state.term is config.term
    assert state.origin_x == config.origin_x
    assert state.origin_y == config.origin_y


def test_Config_select(config):
    """When called, :meth:`Config.select` should change the selected
    setting then return itself.
    """
    config.selected = -1
    state = config.select()
    assert state is config
    assert not state.wrap
    assert not state.data.wrap


def test_Config_up(config):
    """When called, :meth:`Config.up` should decrement
    :attr:`Config.selected` and return itself.
    """
    config.selected = 1
    state = config.up()
    assert state is config
    assert config.selected == 0


def test_Config_up(config):
    """When called, :meth:`Config.up` should decrement
    :attr:`Config.selected` and return itself. If the
    first setting is selected, select the last setting.
    """
    state = config.up()
    assert state is config
    assert config.selected == 1


# Tests for Config input.
def test_Config_input(config):
    """When valid given input, :meth:`Config.input` should return the
    expected command string.
    """
    config.term.inkey.side_effect = [DOWN, UP, 'x', '\n',]
    assert config.input() == ('down',)
    assert config.input() == ('up',)
    assert config.input() == ('exit',)
    assert config.input() == ('select',)


# Tests for Config UI updates.
def test_Config_update_ui(capsys, config, term):
    """When called, :meth:`Config.update_ui` should redraw the UI
    for the config state.
    """
    config.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        term.move(0, 0) + term.bright_white_on_green
        + 'Rule: B3/S23' + term.normal + '\n'
        + term.move(1, 0) + 'Wrap: True\n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + config.menu + term.clear_eol
    )


# Fixtures for Core.
@pt.fixture
def core(grid, term):
    """A :class:`Core` object for testing."""
    return sui.Core(grid, term)


@pt.fixture
def window_core(big_grid, small_term):
    """A :class:`Core` object for testing."""
    core = sui.Core(big_grid, small_term)
    core.origin_x = 1
    core.origin_y = 3
    return core


# Tests for Core initialization.
def test_Core_init(grid, term):
    """When given required parameters, :class:`Core` should return
    an instance with attributes set to the given values.
    """
    required = {
        'data': grid,
        'term': term,
    }
    obj = sui.Core(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]


# Tests for Core commands.
def test_Core_autorun(core):
    """When called, :meth:`Core.autorun` should return an
    :class:`Autorun` object.
    """
    state = core.autorun()
    assert isinstance(state, sui.Autorun)
    assert state.data is core.data
    assert state.term is core.term


def test_Core_autorun_window(window_core):
    """When called, :meth:`Core.autorun` should return an
    :class:`Autorun` object.
    """
    state = window_core.autorun()
    assert isinstance(state, sui.Autorun)
    assert state.data is window_core.data
    assert state.term is window_core.term
    assert state.origin_x == window_core.origin_x
    assert state.origin_y == window_core.origin_y


def test_Core_clear(core):
    """When called, :meth:`Core.clear` should clear the grid
    and return its parent object.
    """
    state = core.clear()
    assert state is core
    assert (core.data._data == np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ], dtype=bool)).all()


def test_core_config(core):
    """When called, :meth:`Core.config` should return a :class:`Config`
    object.
    """
    state = core.config()
    assert isinstance(state, sui.Config)
    assert state.data is core.data
    assert state.term is core.term
    assert state.origin_x == core.origin_x
    assert state.origin_y == core.origin_y


def test_Core_edit(core):
    """When called, :meth:`Core.edit` should return an
    :class:`Edit` object.
    """
    state = core.edit()
    assert isinstance(state, sui.Edit)
    assert state.data is core.data
    assert state.term is core.term


def test_Core_edit_window(window_core):
    """When called, :meth:`Core.edit` should return an
    :class:`Edit` object.
    """
    state = window_core.edit()
    assert isinstance(state, sui.Edit)
    assert state.data is window_core.data
    assert state.term is window_core.term
    assert state.origin_x == window_core.origin_x
    assert state.origin_y == window_core.origin_y


def test_Core_load(core):
    """When called, :meth:`Core.load` should return an
    :class:`Load` object.
    """
    state = core.load()
    assert isinstance(state, sui.Load)
    assert state.data is core.data
    assert state.term is core.term


def test_Core_load_window(window_core):
    """When called, :meth:`Core.load` should return an
    :class:`Load` object.
    """
    state = window_core.load()
    assert isinstance(state, sui.Load)
    assert state.data is window_core.data
    assert state.term is window_core.term
    assert state.origin_x == window_core.origin_x
    assert state.origin_y == window_core.origin_y


def test_Core_next(core):
    """When called, :meth:`Core.next` should advance the grid
    and return its parent object.
    """
    state = core.next()
    assert state is core
    assert (core.data._data == data_next).all()


def test_Core_random(core):
    """When called, :meth:`Core.random` should fill the grid
    with random values and return its parent object.
    """
    core.data.rng = np.random.default_rng(seed=1138)
    state = core.random()
    assert state is core
    assert (core.data._data == np.array([
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [0, 1, 1, 0],
        [1, 0, 1, 0],
    ], dtype=bool)).all()


def test_Core_quit(core):
    """When called, :meth:`Core.quit` should return an
    :class:`End` object.
    """
    state = core.quit()
    assert isinstance(state, sui.End)


def test_Core_rule(core):
    """When called, :meth:`Core.rule` should return a
    :class:`Rule` object.
    """
    state = core.rule()
    assert isinstance(state, sui.Rule)
    assert state.data is core.data
    assert state.term is core.term


def test_Core_rule_window(window_core):
    """When called, :meth:`Core.rule` should return a
    :class:`Rule` object.
    """
    state = window_core.rule()
    assert isinstance(state, sui.Rule)
    assert state.data is window_core.data
    assert state.term is window_core.term
    assert state.origin_x == window_core.origin_x
    assert state.origin_y == window_core.origin_y


def test_Core_save(core):
    """When called, :meth:`Core.save` should return a
    :class:`Save` object.
    """
    state = core.save()
    assert isinstance(state, sui.Save)
    assert state.data is core.data
    assert state.term is core.term


def test_Core_save(window_core):
    """When called, :meth:`Core.save` should return a
    :class:`Save` object.
    """
    state = window_core.save()
    assert isinstance(state, sui.Save)
    assert state.data is window_core.data
    assert state.term is window_core.term
    assert state.origin_x == window_core.origin_x
    assert state.origin_y == window_core.origin_y


# Tests for Core input.
def test_Core_input(core):
    """When valid given input, :meth:`Core.input` should return the
    expected command string.
    """
    core.term.inkey.side_effect = 'aceflnrsq'
    assert core.input() == ('autorun',)
    assert core.input() == ('clear',)
    assert core.input() == ('edit',)
    assert core.input() == ('config',)
    assert core.input() == ('load',)
    assert core.input() == ('next',)
    assert core.input() == ('random',)
    assert core.input() == ('save',)
    assert core.input() == ('quit',)


def test_Core_input_invalid(capsys, core, term):
    """Given invalid input, :meth:`Core.input` should prompt the
    user to try again.
    """
    core.term.inkey.side_effect = ('`', 'c')
    assert core.input() == ('clear',)
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        term.move(4, 0) + term.clear_eol
        + term.move(4, 0) + term.clear_eol
        + term.move(4, 0) + 'Invalid command. Please try again.'
        + term.clear_eol
    )


# Tests for Core UI updates.
def test_Core_update_ui(capsys, core, term):
    """When called, :meth:`Core.update_ui` should redraw the UI
    for the core state.
    """
    core.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        grid_start_lines
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + core.menu + term.clear_eol
    )


# Fixtures for Edit.
@pt.fixture
def edit(grid, term, tmp_path):
    """An :class:`Edit` object for testing."""
    edit = sui.Edit(grid, term)
    edit.path = tmp_path / '.snapshot.txt'
    yield edit


@pt.fixture
def window_edit(big_grid, small_term, tmp_path):
    """An :class:`Edit` object for testing."""
    edit = sui.Edit(big_grid, small_term)
    edit.path = tmp_path / '.snapshot.txt'
    edit.origin_x = 1
    edit.origin_y = 3
    yield edit


# Tests for Edit initialization.
def test_Edit_init(grid, term):
    """When given required parameters, :class:`Edit` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    required = {
        'data': grid,
        'term': term,
    }
    obj = sui.Edit(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]
    assert obj.row == 2
    assert obj.col == 2


# Tests for Edit commands.
def test_Edit_down(capsys, edit, term):
    """When called, :meth:`Edit.down` should subtract one from the row,
    redraw the status, redraw the cursor, and return its parent object.
    """
    state = edit.down()
    captured = capsys.readouterr()
    assert state is edit
    assert repr(captured.out) == repr(
        grid_start_lines
        + term.move(1, 2) + term.green + '\u2584'
        + term.bright_white_on_black + '\n'
    )


def test_Edit_exit(edit):
    """When called, :meth:`Edit.exit` should return a :class:`Core`
    object.
    """
    state = edit.exit()
    assert isinstance(state, sui.Core)
    assert state.data is edit.data
    assert state.term is edit.term


def test_Edit_exit_window(window_edit):
    """When called, :meth:`Edit.exit` should return a :class:`Core`
    object.
    """
    state = window_edit.exit()
    assert isinstance(state, sui.Core)
    assert state.data is window_edit.data
    assert state.term is window_edit.term
    assert state.origin_x == window_edit.origin_x
    assert state.origin_y == window_edit.origin_y


def test_Edit_flip(capsys, edit, term):
    """When called, :meth:`Edit.flip` should flip the selected
    location and return its parent object.
    """
    state = edit.flip()
    captured = capsys.readouterr()
    assert state is edit
    assert (state.data._data == np.array([
        [0, 1, 0, 1],
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 0],
    ], dtype=bool)).all()
    assert repr(captured.out) == repr(
        term_.move(0, 0) + ' \u2580 \u2580\n'
        + term_.move(1, 0) + ' \u2588\u2580 \n'
        + term.move(1, 2) + term.bright_green + '\u2580'
        + term.bright_white_on_black + '\n'
    )


def test_Edit_left(capsys, edit, term):
    """When called, :meth:`Edit.left` should subtract one from the col,
    redraw the status, redraw the cursor, and return its parent object.
    """
    state = edit.left()
    captured = capsys.readouterr()
    assert state is edit
    assert repr(captured.out) == repr(
        term_.move(0, 0) + ' \u2580 \u2580\n'
        + term_.move(1, 0) + ' \u2588  \n'
        + term.move(1, 1) + term.bright_green_on_bright_white + '\u2580'
        + term.bright_white_on_black + '\n'
    )


def test_Edit_right(capsys, edit, term):
    """When called, :meth:`Edit.right` should add one to the col,
    redraw the status, redraw the cursor, and return its parent
    object.
    """
    state = edit.right()
    captured = capsys.readouterr()
    assert state is edit
    assert repr(captured.out) == repr(
        term_.move(0, 0) + ' \u2580 \u2580\n'
        + term_.move(1, 0) + ' \u2588  \n'
        + term.move(1, 3) + term.green + '\u2580'
        + term.bright_white_on_black + '\n'
    )


def test_Edit_restore(edit, term):
    """When called, :meth:`Edit.restore` should load the snapshot file
    and return the parent object.
    """
    edit.path = Path('tests/data/.snapshot.txt')
    state = edit.restore()
    assert state is edit
    assert (edit.data._data == np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 0, 0],
    ], dtype=bool)).all()


def test_Edit_restore_no_snapshot(edit, term, data_start, tmp_path):
    """When called, :meth:`Edit.restore` should load the snapshot file
    and return the parent object. If there is no snapshot, do not change
    the grid.
    """
    edit.path = tmp_path / '.snapshot.txt'
    state = edit.restore()
    assert state is edit
    assert (edit.data._data == data_start).all()


def test_Edit_snapshot(capsys, edit, term):
    """When called, :meth:`Edit.snapshot` should write the grid to
    the snapshot file and return the parent object.
    """
    state = edit.snapshot()
    with open(edit.path) as fh:
        saved = fh.read()
    captured = capsys.readouterr()
    assert state is edit
    assert repr(saved) == repr(
        'X.X\n'
        '...\n'
        'X..\n'
        'X..'
    )
    assert repr(captured.out) == repr(
        term.move(4, 0) + 'Saving...' + term.clear_eol
    )


def test_Edit_up(capsys, edit, term):
    """When called, :meth:`Edit.up` should add one to the row, redraw
    the status, redraw the cursor, and return its parent object.
    """
    state = edit.up()
    captured = capsys.readouterr()
    assert state is edit
    assert repr(captured.out) == repr(
        grid_start_lines
        + term.move(0, 2) + term.green + '\u2584'
        + term.bright_white_on_black + '\n'
    )


# Tests for Edit input.
def test_Edit_input(edit):
    """When given input, :meth:`Edit.input` should return the expected
    command string.
    """
    edit.term.inkey.side_effect = [
        DOWN,
        'e',
        ' ',
        LEFT,
        'r',
        RIGHT,
        's',
        UP,
    ]
    assert edit.input() == ('down',)
    assert edit.input() == ('exit',)
    assert edit.input() == ('flip',)
    assert edit.input() == ('left',)
    assert edit.input() == ('restore',)
    assert edit.input() == ('right',)
    assert edit.input() == ('snapshot',)
    assert edit.input() == ('up',)


# Tests for Edit UI updates.
def test_Edit_update_ui(capsys, edit, term):
    """When called, :meth:`Edit.update_ui` should draw the UI for
    edit mode.
    """
    edit.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        grid_start_lines
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + edit.menu + term.clear_eol
        + term.move(1, 2) + term.green + '\u2580'
        + term.bright_white_on_black + '\n'
    )


# Test for End initialization.
def test_End_init(grid, term):
    """When given required parameters, :class:`End` should return
    an instance with attributes set to the given values.
    """
    required = {}
    obj = sui.End(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]


# Fixtures for Load.
@pt.fixture
def load(grid, term):
    """A :class:`Load` object for testing."""
    load = sui.Load(grid, term)
    load.files = ['spam', 'eggs', 'ham']
    load.path = Path('tests/data')
    return load


@pt.fixture
def window_load(big_grid, small_term):
    """A :class:`Load` object for testing."""
    load = sui.Load(big_grid, small_term)
    load.files = ['spam', 'eggs', 'ham']
    load.path = Path('tests/data')
    load.origin_x = 1
    load.origin_y = 3
    return load


# Tests for Load initialization.
def test_Load_init(grid, term):
    """When given required parameters, :class:`Load` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    required = {
        'data': grid,
        'term': term,
    }
    obj = sui.Load(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]


# Tests for Load commands.
def test_Load_down(load):
    """When called, :meth:`Load.down` should add one to
    :attr:`Load.selected`, rolling over if the number is
    above the number of files, and return the parent object.
    """
    state = load.down()
    assert state is load
    assert load.selected == 1


def test_Load_exit(load):
    """When called, :meth:`Load.exit` should return a :class:`Core`
    object populated with the grid and terminal objects.
    """
    state = load.exit()
    assert isinstance(state, sui.Core)
    assert state.data == load.data
    assert state.term == load.term


def test_Load_exit_window(window_load):
    """When called, :meth:`Load.exit` should return a :class:`Core`
    object populated with the grid and terminal objects.
    """
    state = window_load.exit()
    assert isinstance(state, sui.Core)
    assert state.data == window_load.data
    assert state.term == window_load.term
    assert state.origin_x == window_load.origin_x
    assert state.origin_y == window_load.origin_y


def test_Load_file(load):
    """When called, :meth:`Load.file` should return a :class:`Load`
    object pointed at the current working directory.
    """
    state = load.file()
    assert isinstance(state, sui.Load)
    assert state.data is load.data
    assert state.term is load.term
    assert state.path == Path.cwd()


def test_Load_load(load):
    """When called, :meth:`Load.load` should load the selected file
    and return a :class:`Core` object.
    """
    state = load.load()
    assert isinstance(state, sui.Core)
    assert state.data is load.data
    assert state.term is load.term
    assert (state.data._data == np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 0, 0],
    ], dtype=bool)).all()


def test_Load_load_directory(load):
    """When called with a directory selected, :meth:`Load.load` should
    load the selected directory in :class:`Load` object and return it.
    """
    load.path = Path('tests/data')
    load._get_files()
    load.selected = 1
    state = load.load()
    assert isinstance(state, sui.Load)
    assert state.data is load.data
    assert state.term is load.term
    assert state.path == Path('tests/data/zeggs')
    assert state.selected == 0


def test_Load_load_window(window_load):
    """When called, :meth:`Load.load` should load the selected file
    and return a :class:`Core` object.
    """
    state = window_load.load()
    assert isinstance(state, sui.Core)
    assert state.data is window_load.data
    assert state.term is window_load.term
    assert state.origin_x == window_load.origin_x
    assert state.origin_y == window_load.origin_y
    assert (state.data._data == np.array([
        [0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ], dtype=bool)).all()


def test_Load_up(load):
    """When called, :meth:`Load.up` should subtract one from
    :attr:`Load.selected`, rolling over if the number is
    above the number of files, and return the parent object.
    If the select would go above the top of the list, roll
    it around to the bottom of the list.
    """
    state = load.up()
    assert state is load
    assert load.selected == 2


# Tests for Load input.
def test_Load_input(load):
    """When given input, :meth:`Load.input` should return the expected
    command string.
    """
    load.term.inkey.side_effect = [DOWN, 'e', 'f', '\n', UP]
    assert load.input() == ('down',)
    assert load.input() == ('exit',)
    assert load.input() == ('file',)
    assert load.input() == ('load',)
    assert load.input() == ('up',)


# Tests for Load UI updates.
def test_Load_update_ui(capsys, load, term):
    """When called, :meth:`Load.update_ui` should draw the UI for
    load mode.
    """
    load.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        term.move(0, 0) + term.on_green + '▸ ..'
        + term.normal + term.clear_eol + '\n'
        + term.move(1, 0) + '▸ zeggs' + term.clear_eol + '\n'
        + term.move(2, 0) + '.snapshot.txt' + term.clear_eol + '\n'
        + term.move(3, 0) + 'spam' + term.clear_eol + '\n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + load.menu + term.clear_eol
    )


# Fixtures for Rule.
@pt.fixture
def rule(grid, term):
    """A :class:`Rule` object for testing."""
    return sui.Rule(grid, term)


@pt.fixture
def window_rule(big_grid, small_term):
    """A :class:`Rule` object for testing."""
    return sui.Rule(big_grid, small_term)


# Tests for Rule initialization.
def test_Rule_init(grid, term):
    """When given required parameters, :class:`Rule` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    required = {
        'data': grid,
        'term': term,
    }
    obj = sui.Rule(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]


# Tests for Rule commands.
def test_Rule_change(rule):
    """When given a rule, :meth:`Rule.change` should change the rules
    of the grid and return an :class:`Core` object with the grid and
    terminal objects.
    """
    state = rule.change('B36/S23')
    assert isinstance(state, sui.Core)
    assert state.data is rule.data
    assert state.term is rule.term
    assert rule.data.rule == 'B36/S23'


def test_Rule_change_window(window_rule):
    """When given a rule, :meth:`Rule.change` should change the rules
    of the grid and return an :class:`Core` object with the grid and
    terminal objects.
    """
    state = window_rule.change('B36/S23')
    assert isinstance(state, sui.Core)
    assert state.data is window_rule.data
    assert state.term is window_rule.term
    assert window_rule.data.rule == 'B36/S23'
    assert state.origin_x == window_rule.origin_x
    assert state.origin_y == window_rule.origin_y


def test_Rule_exit(rule):
    """When called, :meth:`Rule.exit` should return a :class:`Core`
    object populated with the grid and terminal objects.
    """
    state = rule.exit()
    assert isinstance(state, sui.Core)
    assert state.data == rule.data
    assert state.term == rule.term


def test_Rule_exit_window(window_rule):
    """When called, :meth:`Rule.exit` should return a :class:`Core`
    object populated with the grid and terminal objects.
    """
    state = window_rule.exit()
    assert isinstance(state, sui.Core)
    assert state.data == window_rule.data
    assert state.term == window_rule.term
    assert state.origin_x == window_rule.origin_x
    assert state.origin_y == window_rule.origin_y


# Tests for Rule input.
def test_Rule_input(mocker, rule):
    """When given input, :meth:`Rule.input` should return the expected
    command string.
    """
    mocker.patch('life.sui.input', side_effect=['B0/S0', ''])
    assert rule.input() == ('change', 'B0/S0')
    assert rule.input() == ('exit',)


# Tests for Rule UI updates.
def test_Rule_update_ui(capsys, rule, term):
    """When called, :meth:`Rule.update_ui` should redraw the UI
    for the rule state.
    """
    rule.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        grid_start_lines
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + rule.menu + term.clear_eol
    )


# Fixtures for Save tests.
@pt.fixture
def save(grid, term, tmp_path):
    save = sui.Save(grid, term)
    save.path = tmp_path
    yield save


@pt.fixture
def window_save(big_grid, small_term, tmp_path):
    save = sui.Save(big_grid, small_term)
    save.path = tmp_path
    yield save


# Tests for Save initialization.
def test_Save_init_all_defaults(grid, term):
    """When given required parameters, :class:`Save` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    required = {
        'data': grid,
        'term': term,
    }
    optional = {
        'origin_x': 0,
        'origin_y': 0,
    }
    obj = sui.Start(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]
    for attr in optional:
        assert getattr(obj, attr) == optional[attr]


def test_Save_init_all_optionals(grid, term):
    """When given optional parameters, :class:`Save` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    optional = {
        'data': grid,
        'term': term,
        'origin_x': 2,
        'origin_y': 3,
    }
    obj = sui.Start(**optional)
    for attr in optional:
        assert getattr(obj, attr) == optional[attr]


# Tests for Save commands.
def test_Save_save(save):
    """Given a filename, :meth:`Save.save` should save the current
    grid to a file and return a :class:`Core` object.
    """
    state = save.save('spam')
    with open(save.path / 'spam') as fh:
        saved = fh.read()
    assert isinstance(state, sui.Core)
    assert state.data is save.data
    assert state.term is save.term
    assert repr(saved) == repr(
        'X.X\n'
        '...\n'
        'X..\n'
        'X..'
    )


def test_Save_save_window(window_save):
    """Given a filename, :meth:`Save.save` should save the current
    grid to a file and return a :class:`Core` object.
    """
    state = window_save.save('spam')
    with open(window_save.path / 'spam') as fh:
        saved = fh.read()
    assert isinstance(state, sui.Core)
    assert state.data is window_save.data
    assert state.term is window_save.term
    assert state.origin_x == window_save.origin_x
    assert state.origin_y == window_save.origin_y
    assert repr(saved) == repr(
        '.X.X.X\n'
        'X.X.X.\n'
        '.X.X.X\n'
        'X.X.X.\n'
        '.X.X.X\n'
        'X.X.X.'
    )


# Tests for Save input.
def test_Save_input(mocker, save):
    """When given input, :meth:`Save.input` should return the expected
    command string.
    """
    mocker.patch('life.sui.input', side_effect=['spam'])
    assert save.input() == ('save', 'spam')


# Tests for Save UI updates.
def test_Save_update_ui(capsys, mocker, save, term):
    """When called, :meth:`Save.update_ui` should redraw the UI
    for the save state.
    """
    mocker.patch('pathlib.Path.iterdir', return_value=['spam', 'eggs'])
    save.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        term.move(0, 0) + 'eggs' + term.clear_eol + '\n'
        + term.move(1, 0) + 'spam' + term.clear_eol + '\n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + save.menu + term.clear_eol
    )


def test_Save_update_ui_clear_lines(capsys, mocker, save, term):
    """When called, :meth:`Save.update_ui` should redraw the UI
    for the save state.
    """
    mocker.patch('pathlib.Path.iterdir', return_value=['spam',])
    save.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        term.move(0, 0) + 'spam' + term.clear_eol + '\n'
        + term.move(1, 0) + term.clear_eol + '\n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + save.menu + term.clear_eol
    )


# Fixtures for Start.
@pt.fixture
def start(grid, term):
    """A :class:`Start` object for testing."""
    start = sui.Start(grid, term)
    return start


@pt.fixture
def window_start(big_grid, small_term):
    """A :class:`Start` object with a window for testing."""
    start = sui.Start(big_grid, small_term)
    start.origin_x = 1
    start.origin_y = 3
    return start


# Tests for Start initialization.
def test_Start_init_all_default(term):
    """Given no parameters, :class:`Start` should initialize an
    instance of itself using default attribute values.
    """
    start = sui.Start()
    assert start.data.width == term.width
    assert start.data.height == (term.height - 3) * 2
    assert start.origin_y == 0
    assert start.origin_x == 0
    assert start.rule == 'B3/S23'
    assert start.wrap
    assert isinstance(start.term, blessed.Terminal)


def test_Start_init_all_optionals(grid, term):
    """When given optional parameters, :class:`Start` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    optionals = {
        'data': grid,
        'term': term,
        'origin_x': 2,
        'origin_y': 3,
        'rule': 'B36/S23',
        'wrap': False,
    }
    obj = sui.Start(**optionals)
    for attr in optionals:
        assert getattr(obj, attr) is optionals[attr]


def test_Start_init_big_grid(big_grid, small_term):
    """Given a grid bigger than the terminal, :class:`Start` should
    initialize an instance of itself using the given grid. The origin
    for the window should be set to the middle of the grid.
    """
    start = sui.Start(big_grid, small_term)
    assert start.origin_y == 2
    assert start.origin_x == 2


def test_Start_init_file(term):
    """Given a path to a file, :class:`Start` should generate a grid
    from the contents of the file.
    """
    start = sui.Start(term=term, file='tests/data/spam')
    assert start.file == 'tests/data/spam'
    assert (start.data._data == np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 0, 0],
    ], dtype=bool)).all()


def test_Start_init_no_wrap():
    """Given wrap of `False`, :class:`Start` should generate a grid
    then set the grid's wrap to `False`.
    """
    start = sui.Start(wrap=False)
    assert not start.data.wrap


def test_Start_init_rule():
    """Given a valid rule string, :class:`Start` should generate a grid
    then set the grid's rule to the given value.
    """
    start = sui.Start(rule='B36/S23')
    assert start.data.rule == 'B36/S23'


# Tests for Start commands.
def test_Start_run(start):
    """When called, :meth:`Start.run` should always return a
    :class:`Core` object initialized with the parent object's
    grid and term.
    """
    state = start.run()
    assert isinstance(state, sui.Core)
    assert state.data is start.data
    assert state.term is start.term


def test_Start_run_window(window_start):
    """When called, :meth:`Start.run` should always return a
    :class:`Core` object initialized with the parent object's
    grid and term. If grid is larger than the terminal, the
    origin of the window should be initialized with the parent
    objects values.
    """
    state = window_start.run()
    assert isinstance(state, sui.Core)
    assert state.data is window_start.data
    assert state.term is window_start.term
    assert state.origin_x == window_start.origin_x
    assert state.origin_y == window_start.origin_y


# Tests for Start input.
def test_Start_input(capsys, start, term):
    """When valid given input, :meth:`Start.input` should return the
    expected command string.
    """
    start.term.inkey.side_effect = ' '
    captured = capsys.readouterr()
    assert start.input() == ('run',)


# Tests for Start UI updates.
def test_Start_update_ui(capsys, start, term):
    """When called, :meth:`Start.update_ui` should redraw the UI
    for the start state.
    """
    start.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        grid_start_lines
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + start.menu + term.clear_eol
    )


# Tests for cells.
def test_cells():
    """Given the contents of a .cells file, :func:`cells` should
    return an array containing the data from the file.
    """
    assert (sui.cells([
        '!comment\n',
        '.O.\n',
        'O.O\n',
        '.O.\n',
    ]) == np.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ], dtype=bool)).all()


# Tests for main.
def test_main_simple_loop(mocker):
    """The :funct:`main` loop should start and end a game of life."""
    mocker.patch('sys.argv', ['life',])
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    sui.main()


def test_main_f(mocker):
    """When invoked from the command line with `-f` followed by a
    the path to a valid pattern file, :func:`main` should create a
    :class:`Start` object with :attr:`Start.file` set to the given
    path.
    """
    start = sui.Start()
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-f tests/data/spam'])
    sui.main()
    assert mock_start.call_args[1]['file'] == 'tests/data/spam'


def test_main_r(mocker):
    """When invoked from the command line with `-r` followed by a
    valid rule string, :func:`main` should create a :class:`Start`
    object with :attr:`Start.rule` set to the given rule string.
    """
    start = sui.Start()
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-r B36/S23'])
    sui.main()
    assert mock_start.call_args[1]['rule'] == 'B36/S23'


def test_main_W(mocker):
    """When invoked from the command line with `-W`, :func:`main`
    should create a :class:`Start` object with :attr:`Start.wrap`
    set to `False`.
    """
    start = sui.Start()
    mock_start = mocker.patch('life.sui.Start', return_value=start)
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    mocker.patch('sys.argv', ['life', '-W'])
    sui.main()
    assert mock_start.call_args[1]['wrap'] is False
