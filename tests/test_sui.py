"""
test_sui
~~~~~~~

This provides the unit tests for life.sui.py.
"""
import unittest as ut
from pathlib import Path
from unittest.mock import call, patch, PropertyMock

import blessed
import numpy as np
import pytest as pt

from life import life
from life import sui


# Terminal keys:
DOWN = '\x1b[B'
UP = '\x1b[A'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'


# Common fixtures.
@pt.fixture
def grid():
    """A :class:`Grid` object for testing."""
    grid = life.Grid(4, 3)
    grid._data[0, 1] = True
    grid._data[0, 3] = True
    grid._data[2, 1] = True
    return grid


@pt.fixture
def term(mocker):
    """A :class:`blessed.Terminal` object for testing."""
    mocker.patch('blessed.Terminal.inkey')
    return blessed.Terminal()


# Fixtures for Autorun.
@pt.fixture
def autorun(grid, term):
    return sui.Autorun(grid, term)


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


def test_Autorun_run(autorun):
    """When called, :meth:`Autorun.run` should advance the grid and
    return the :class:`Autorun` object.
    """
    state = autorun.run()
    assert state is autorun
    assert (autorun.data._data == np.array([
        [1, 0, 1, 0],
        [1, 0, 1, 0],
        [1, 0, 1, 0],
    ], dtype=bool)).all()


# Tests for Autorun UI updates.
def test_Autorun_update_ui(capsys, autorun, term):
    """When called, :meth:`Autorun.update_ui` should redraw the UI."""
    autorun.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + autorun.menu + term.clear_eol
    )


# Fixtures for Core.
@pt.fixture
def core(grid, term):
    """A :class:`Core` object for testing."""
    return sui.Core(grid, term)


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


# Tests for Core input.
def test_Core_input(core):
    """When valid given input, :meth:`Core.input` should return the
    expected command string.
    """
    core.term.inkey.side_effect = 'acelnrusq'
    assert core.input() == ('autorun',)
    assert core.input() == ('clear',)
    assert core.input() == ('edit',)
    assert core.input() == ('load',)
    assert core.input() == ('next',)
    assert core.input() == ('random',)
    assert core.input() == ('rule',)
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


# Tests for Core commands.
def test_Core_autorun(core):
    """When called, :meth:`Core.autorun` should return an
    :class:`Autorun` object.
    """
    state = core.autorun()
    assert isinstance(state, sui.Autorun)


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
    ], dtype=bool)).all()


def test_Core_edit(core):
    """When called, :meth:`Core.edit` should return an
    :class:`Edit` object.
    """
    state = core.edit()
    assert isinstance(state, sui.Edit)


def test_Core_load(core):
    """When called, :meth:`Core.load` should return an
    :class:`Load` object.
    """
    state = core.load()
    assert isinstance(state, sui.Load)


def test_Core_next(core):
    """When called, :meth:`Core.next` should advance the grid
    and return its parent object.
    """
    state = core.next()
    assert state is core
    assert (core.data._data == np.array([
        [1, 0, 1, 0],
        [1, 0, 1, 0],
        [1, 0, 1, 0],
    ], dtype=bool)).all()


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


def test_Core_save(core):
    """When called, :meth:`Core.save` should return a
    :class:`Save` object.
    """
    state = core.save()
    assert isinstance(state, sui.Save)


# Tests for Core UI updates.
def test_Core_update_ui(capsys, core, term):
    """When called, :meth:`Core.update_ui` should redraw the UI
    for the core state.
    """
    core.update_ui()
    captured = capsys.readouterr()
    assert repr(captured.out) == repr(
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
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
    assert obj.row == 1
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
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(1, 2) + term.green + '\u2580'
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


def test_Edit_flip(capsys, edit, term):
    """When called, :meth:`Edit.flip` should flip the selected
    location and return its parent object.
    """
    state = edit.flip()
    captured = capsys.readouterr()
    assert state is edit
    assert (state.data._data == np.array([
        [0, 1, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
    ], dtype=bool)).all()
    assert repr(captured.out) == repr(
        term.move(0, 0) + ' ▀▄▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(0, 2) + term.bright_green + '\u2584'
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
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(0, 1) + term.green_on_bright_white + '\u2584'
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
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(0, 3) + term.green_on_bright_white + '\u2584'
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
    ], dtype=bool)).all()


def test_Edit_restore_no_snapshot(edit, term, tmp_path):
    """When called, :meth:`Edit.restore` should load the snapshot file
    and return the parent object. If there is no snapshot, do not change
    the grid.
    """
    edit.path = tmp_path / '.snapshot.txt'
    state = edit.restore()
    assert state is edit
    assert (edit.data._data == np.array([
        [0, 1, 0, 1],
        [0, 0, 0, 0],
        [0, 1, 0, 0],
    ], dtype=bool)).all()


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
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(0, 2) + term.green + '\u2580'
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
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + edit.menu + term.clear_eol
        + term.move(0, 2) + term.green + '\u2584'
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
    assert (load.data._data == np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
    ], dtype=bool)).all()


def test_Load_load_directory(load):
    """When called with a directory selected, :meth:`Load.load` should
    load the selected directory in :class:`Load` object and return it.
    """
    load.path = Path('tests')
    load._get_files()
    state = load.load()
    assert isinstance(state, sui.Load)
    assert state.data is load.data
    assert state.term is load.term
    assert state.path == Path('tests/data')


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
        term.move(0, 0) + term.on_green + '.snapshot.txt'
        + term.normal + term.clear_eol + '\n'
        + term.move(1, 0) + 'spam' + term.clear_eol + '\n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + load.menu + term.clear_eol
    )


# Fixtures for Rule.
@pt.fixture
def rule(grid, term):
    """A :class:`Rule` object for testing."""
    return sui.Rule(grid, term)


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


def test_Rule_exit(rule):
    """When called, :meth:`Rule.exit` should return a :class:`Core`
    object populated with the grid and terminal objects.
    """
    state = rule.exit()
    assert isinstance(state, sui.Core)
    assert state.data == rule.data
    assert state.term == rule.term


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
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + rule.menu + term.clear_eol
    )


# Fixtures for Save tests.
@pt.fixture
def save(grid, term, tmp_path):
    save = sui.Save(grid, term)
    save.path = tmp_path
    yield save


# Tests for Save initialization.
def test_Save_init(grid, term):
    """When given required parameters, :class:`Save` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    required = {
        'data': grid,
        'term': term,
    }
    obj = sui.Start(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]


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
        'X..'
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


# Tests for Start initialization.
def test_Start_init_default(term):
    """Given no parameters, :class:`Start` should initialize an
    instance of itself using default attribute values.
    """
    start = sui.Start()
    assert start.data.width == term.width
    assert start.data.height == (term.height - 3) * 2
    assert isinstance(start.term, blessed.Terminal)


def test_Start_init_optionals(grid, term):
    """When given optional parameters, :class:`Start` should return
    an instance with attributes set to the given values. It should
    also initialize the cursor position.
    """
    optionals = {
        'data': grid,
        'term': term,
    }
    obj = sui.Start(**optionals)
    for attr in optionals:
        assert getattr(obj, attr) is optionals[attr]


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
        term.move(0, 0) + ' ▀ ▀\n'
        + term.move(1, 0) + ' ▀  \n'
        + term.move(2, 0) + '\u2500' * 4 + '\n'
        + term.move(3, 0) + start.menu + term.clear_eol
    )


# Tests for main.
def test_main_simple_loop(mocker):
    """The :funct:`main` loop should start and end a game of life."""
    mocker.patch('blessed.Terminal.inkey', side_effect=[' ', 'q'])
    sui.main()
