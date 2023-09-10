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
ESC = '\x1b'
DOWN = '\x1b[B'
UP = '\x1b[A'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'
SDOWN = '\x1b[1;2B'
SUP = '\x1b[1;2A'
SLEFT = '\x1b[1;2D'
SRIGHT = '\x1b[1;2C'

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
def grid_40(data_start):
    """A :class:`Grid` object for testing."""
    grid = life.Grid(40, 40)
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
def term_40(mocker):
    """A :class:`blessed.Terminal` object for testing."""
    mocker.patch('blessed.Terminal.inkey')
    mocker.patch(
        'blessed.Terminal.height',
        return_value=40,
        new_callable=mocker.PropertyMock
    )
    mocker.patch(
        'blessed.Terminal.width',
        return_value=40,
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


# Tests for Autorun.
class TestAutorun():
    # Fixtures for Autorun.
    @pt.fixture
    def autorun(self, grid, term):
        """An :class:`Autorun` object for testing."""
        return sui.Autorun(grid, term)

    @pt.fixture
    def window_autorun(self, big_grid, small_term):
        """An :class:`Autorun` object for testing windowing."""
        autorun = sui.Autorun(big_grid, small_term)
        autorun.origin_x = 1
        autorun.origin_y = 3
        return autorun

    # Tests for Autorun initialization.
    def test_Autorun_init(self, grid, term):
        """When given required parameters, :class:`Autorun` should return
        an instance with attributes set to the given values.
        """
        required = {
            'data': grid,
            'term': term,
        }
        optional = {
            'origin_x': 0,
            'origin_y': 0,
            'pace': 0,
        }
        obj = sui.Autorun(**required)
        for attr in required:
            assert getattr(obj, attr) is required[attr]
        for attr in optional:
            assert getattr(obj, attr) is optional[attr]

    # Tests for Autorun input.
    def test_Autorun_input(self, autorun):
        """If a key is pressed, :meth:`Autorun.input` should return an
        command string.
        """
        autorun.term.inkey.side_effect = [LEFT, RIGHT, 'x',]
        assert autorun.input() == ('slower',)
        assert autorun.input() == ('faster',)
        assert autorun.input() == ('exit',)

    def test_Autorun_input_timeout(self, autorun):
        """If no key is pressed, :meth:`Autorun.input` should return a
        run command string.
        """
        autorun.term.inkey.return_value = ''
        assert autorun.input() == ('run',)

    # Tests for Autorun commands.
    def test_Autorun_exit(self, autorun):
        """When called :func:`Autorun.exit` should return a :class:`Core`
        object populated with its :class:`Grid` and :class:`blessed.Terminal`
        objects.
        """
        state = autorun.exit()
        assert isinstance(state, sui.Core)
        assert state.data is autorun.data
        assert state.term is autorun.term

    def test_Autorun_exit(self, window_autorun):
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

    def test_Autorun_faster(self, autorun):
        """When called :func:`Autorun.faster` should decrement the pace
        and return itself.
        """
        autorun.pace = 0.03
        state = autorun.faster()
        assert state is autorun
        assert state.pace == 0.03 - 0.01

    def test_Autorun_run(self, autorun):
        """When called, :meth:`Autorun.run` should advance the grid and
        return the :class:`Autorun` object.
        """
        state = autorun.run()
        assert state is autorun
        assert (autorun.data._data == data_next).all()

    def test_Autorun_run_pace(self, mocker, autorun):
        """When called, :meth:`Autorun.run` should advance the grid and
        return the :class:`Autorun` object.
        """
        mock_sleep = mocker.patch('life.sui.sleep')
        autorun.pace = 0.01
        state = autorun.run()
        assert state is autorun
        assert (autorun.data._data == data_next).all()
        assert mock_sleep.mock_calls == [
            mocker.call(0.01),
        ]

    def test_Autorun_slower(self, autorun):
        """When called :func:`Autorun.slower` should increment the pace
        and return itself.
        """
        autorun.pace = 0.03
        state = autorun.slower()
        assert state is autorun
        assert state.pace == 0.03 + 0.01

    # Tests for Autorun UI updates.
    def test_Autorun_update_ui(self, capsys, autorun, term):
        """When called, :meth:`Autorun.update_ui` should redraw the UI."""
        autorun.update_ui()
        captured = capsys.readouterr()
        assert repr(captured.out) == repr(
            grid_start_lines
            + term.move(2, 0) + '\u2500' * 4 + '\n'
            + term.move(3, 0) + autorun.menu + term.clear_eol
        )


# Tests for Config.
class TestConfig:
    # Fixtures for Config.
    @pt.fixture
    def config(self, grid, term):
        """A :class:`Config` object for testing."""
        config = sui.Config(grid, term)
        return config

    # Tests for Config initialization.
    def test_Config_init_all_defaults(self, grid, term):
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

    def test_Config_init_all_optional(self, grid, term):
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
    def test_Config_down(self, config):
        """When called, :meth:`Config.down` should increment
        :attr:`Config.selected` and return itself.
        """
        state = config.down()
        assert state is config
        assert config.selected == 1

    def test_Config_down_wrap(self, config):
        """When called, :meth:`Config.down` should increment
        :attr:`Config.selected` and return itself. If down is
        called when the last setting is selected, select the
        first setting.
        """
        config.selected = len(config.settings) - 1
        state = config.down()
        assert state is config
        assert config.selected == 0

    def test_Config_exit(self, config):
        """When called, :meth:`Config.exit` should return a
        :class:`Core` object.
        """
        state = config.exit()
        assert isinstance(state, sui.Core)
        assert state.data is config.data
        assert state.term is config.term
        assert state.origin_x == config.origin_x
        assert state.origin_y == config.origin_y

    def test_Config_select_pace(self, config):
        """When called, :meth:`Config.select` should set
        :attr:`Config.pace` and return the parent object.
        """
        config.term.inkey.side_effect = [
            '0', '.', '0', '9', '\n',
        ]
        config.selected = 0
        state = config.select()
        assert state is config
        assert state.data is config.data
        assert state.term is config.term
        assert state.origin_x == config.origin_x
        assert state.origin_y == config.origin_y
        assert state.pace == 0.09

    def test_Config_select_rule(self, config):
        """When called, :meth:`Config.select` should set
        :attr:`Config.rule` and return the parent object.
        """
        config.term.inkey.side_effect = [
            'B', '3', '6', '/', 'S', '2', '3', '\n',
        ]
        config.selected = 1
        state = config.select()
        assert state is config
        assert state.data is config.data
        assert state.term is config.term
        assert state.origin_x == config.origin_x
        assert state.origin_y == config.origin_y
        assert state.rule == 'B36/S23'

    def test_Config_select_rule_invalid(self, config):
        """When called, :meth:`Config.select` should set
        :attr:`Config.rule` and return the parent object.
        If an invalid value is given, prompt the user to
        try again.
        """
        config.term.inkey.side_effect = [
            's', 'p', 'a', 'm', '\n',
            'B', '3', '6', '/', 'S', '2', '3', '\n',
        ]
        config.selected = 1
        state = config.select()
        assert state is config
        assert state.data is config.data
        assert state.term is config.term
        assert state.origin_x == config.origin_x
        assert state.origin_y == config.origin_y
        assert state.rule == 'B36/S23'

    def test_Config_select_wrap(self, config):
        """When called, :meth:`Config.select` should change the selected
        setting then return itself.
        """
        config.selected = -1
        state = config.select()
        assert state is config
        assert not state.wrap
        assert not state.data.wrap

    def test_Config_up(self, config):
        """When called, :meth:`Config.up` should decrement
        :attr:`Config.selected` and return itself.
        """
        config.selected = 1
        state = config.up()
        assert state is config
        assert config.selected == 0

    def test_Config_up_from_top(self, config):
        """When called, :meth:`Config.up` should decrement
        :attr:`Config.selected` and return itself. If the
        first setting is selected, select the last setting.
        """
        state = config.up()
        assert state is config
        assert config.selected == len(config.settings) - 1

    # Tests for Config input.
    def test_Config_input(self, config):
        """When valid given input, :meth:`Config.input` should return the
        expected command string.
        """
        config.term.inkey.side_effect = [DOWN, UP, 'x', '\n',]
        assert config.input() == ('down',)
        assert config.input() == ('up',)
        assert config.input() == ('exit',)
        assert config.input() == ('select',)

    # Tests for Config UI updates.
    def test_Config_update_ui(self, capsys, config, term):
        """When called, :meth:`Config.update_ui` should redraw the UI
        for the config state.
        """
        config.update_ui()
        captured = capsys.readouterr()
        assert repr(captured.out) == repr(
            term.move(0, 0) + term.black_on_green
            + 'Pace: 0' + term.clear_eol + term.normal + '\n'
            + term.move(1, 0) + 'Rule: B3/S23' + term.clear_eol + '\n'
            + term.move(2, 0) + 'Wrap: True' + term.clear_eol + '\n'
            + term.move(2, 0) + '\u2500' * 4 + '\n'
            + term.move(3, 0) + config.menu + term.clear_eol
        )


# Tests for Core.
class TestCore:
    # Fixtures for Core.
    @pt.fixture
    def core(self, grid, term):
        """A :class:`Core` object for testing."""
        return sui.Core(grid, term)

    @pt.fixture
    def window_core(self, big_grid, small_term):
        """A :class:`Core` object for testing."""
        core = sui.Core(big_grid, small_term)
        core.origin_x = 1
        core.origin_y = 3
        return core

    # Tests for Core initialization.
    def test_Core_init(self, grid, term):
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
    def test_Core_autorun(self, core):
        """When called, :meth:`Core.autorun` should return an
        :class:`Autorun` object.
        """
        state = core.autorun()
        assert isinstance(state, sui.Autorun)
        assert state.data is core.data
        assert state.term is core.term

    def test_Core_autorun_window(self, window_core):
        """When called, :meth:`Core.autorun` should return an
        :class:`Autorun` object.
        """
        window_core.pace = 0.01
        state = window_core.autorun()
        assert isinstance(state, sui.Autorun)
        assert state.data is window_core.data
        assert state.term is window_core.term
        assert state.origin_x == window_core.origin_x
        assert state.origin_y == window_core.origin_y
        assert state.pace == 0.01

    def test_Core_clear(self, core):
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

    def test_core_config(self, core):
        """When called, :meth:`Core.config` should return a :class:`Config`
        object.
        """
        state = core.config()
        assert isinstance(state, sui.Config)
        assert state.data is core.data
        assert state.term is core.term
        assert state.origin_x == core.origin_x
        assert state.origin_y == core.origin_y

    def test_Core_edit(self, core):
        """When called, :meth:`Core.edit` should return an
        :class:`Edit` object.
        """
        state = core.edit()
        assert isinstance(state, sui.Edit)
        assert state.data is core.data
        assert state.term is core.term

    def test_Core_edit_window(self, window_core):
        """When called, :meth:`Core.edit` should return an
        :class:`Edit` object.
        """
        state = window_core.edit()
        assert isinstance(state, sui.Edit)
        assert state.data is window_core.data
        assert state.term is window_core.term
        assert state.origin_x == window_core.origin_x
        assert state.origin_y == window_core.origin_y

    def test_Core_load(self, core):
        """When called, :meth:`Core.load` should return an
        :class:`Load` object.
        """
        state = core.load()
        assert isinstance(state, sui.Load)
        assert state.data is core.data
        assert state.term is core.term

    def test_Core_load_window(self, window_core):
        """When called, :meth:`Core.load` should return an
        :class:`Load` object.
        """
        state = window_core.load()
        assert isinstance(state, sui.Load)
        assert state.data is window_core.data
        assert state.term is window_core.term
        assert state.origin_x == window_core.origin_x
        assert state.origin_y == window_core.origin_y

    def test_Core_next(self, core):
        """When called, :meth:`Core.next` should advance the grid
        and return its parent object.
        """
        state = core.next()
        assert state is core
        assert (core.data._data == data_next).all()

    def test_Core_random(self, core):
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

    def test_Core_quit(self, core):
        """When called, :meth:`Core.quit` should return an
        :class:`End` object.
        """
        state = core.quit()
        assert isinstance(state, sui.End)

    def test_Core_save(self, core):
        """When called, :meth:`Core.save` should return a
        :class:`Save` object.
        """
        state = core.save()
        assert isinstance(state, sui.Save)
        assert state.data is core.data
        assert state.term is core.term

    def test_Core_save(self, window_core):
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
    def test_Core_input(self, core):
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

    def test_Core_input_invalid(self, capsys, core, term):
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
    def test_Core_update_ui(self, capsys, core, term):
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


# Tests for Edit.
class TestEdit:
    # Fixtures for Edit.
    @pt.fixture
    def edit(self, grid, term, tmp_path):
        """An :class:`Edit` object for testing."""
        edit = sui.Edit(grid, term)
        edit.path = tmp_path / '.snapshot.txt'
        yield edit

    @pt.fixture
    def edit_40(self, grid_40, term_40, tmp_path):
        """An :class:`Edit` object for testing."""
        edit = sui.Edit(grid_40, term_40)
        edit.path = tmp_path / '.snapshot.txt'
        yield edit

    @pt.fixture
    def window_edit(self, big_grid, small_term, tmp_path):
        """An :class:`Edit` object for testing."""
        edit = sui.Edit(big_grid, small_term)
        edit.path = tmp_path / '.snapshot.txt'
        edit.origin_x = 1
        edit.origin_y = 3
        yield edit

    # Tests for Edit initialization.
    def test_Edit_init(self, grid, term):
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
    def test_Edit_down(self, capsys, edit, term):
        """When called, :meth:`Edit.down` should add one from the row,
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

    def test_Edit_down_10(self, edit_40):
        """When called with ten, :meth:`Edit.down` should add ten to the
        row, redraw the status, redraw the cursor, and return its parent
        object.
        """
        state = edit_40.down(10)
        assert state is edit_40
        assert state.row == 30
        assert state.col == 20

    def test_Edit_exit(self, edit):
        """When called, :meth:`Edit.exit` should return a :class:`Core`
        object.
        """
        state = edit.exit()
        assert isinstance(state, sui.Core)
        assert state.data is edit.data
        assert state.term is edit.term

    def test_Edit_exit_window(self, window_edit):
        """When called, :meth:`Edit.exit` should return a :class:`Core`
        object.
        """
        state = window_edit.exit()
        assert isinstance(state, sui.Core)
        assert state.data is window_edit.data
        assert state.term is window_edit.term
        assert state.origin_x == window_edit.origin_x
        assert state.origin_y == window_edit.origin_y

    def test_Edit_flip(self, capsys, edit, term):
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

    def test_Edit_left(self, capsys, edit, term):
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

    def test_Edit_left_10(self, edit_40):
        """When called with ten, :meth:`Edit.left` should subtract ten
        from the col, redraw the status, redraw the cursor, and return
        its parent object.
        """
        state = edit_40.left(10)
        assert state is edit_40
        assert state.row == 20
        assert state.col == 10

    def test_Edit_right(self, capsys, edit, term):
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

    def test_Edit_right_10(self, edit_40):
        """When called with 10, :meth:`Edit.right` should add ten to the
        col, redraw the status, redraw the cursor, and return its parent
        object.
        """
        state = edit_40.right(10)
        assert state is edit_40
        assert state.row == 20
        assert state.col == 30

    def test_Edit_restore(self, edit, term):
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

    def test_Edit_restore_no_snapshot(self, edit, term, data_start, tmp_path):
        """When called, :meth:`Edit.restore` should load the snapshot file
        and return the parent object. If there is no snapshot, do not change
        the grid.
        """
        edit.path = tmp_path / '.snapshot.txt'
        state = edit.restore()
        assert state is edit
        assert (edit.data._data == data_start).all()

    def test_Edit_snapshot(self, capsys, edit, term):
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

    def test_Edit_up(self, capsys, edit, term):
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

    def test_Edit_up_10(self, edit_40):
        """When called with 10, :meth:`Edit.up` should subtract ten from
        the row, redraw the status, redraw the cursor, and return its parent
        object.
        """
        state = edit_40.up(10)
        assert state is edit_40
        assert state.row == 10
        assert state.col == 20

    # Tests for Edit input.
    def test_Edit_input(self, edit, term):
        """When given input, :meth:`Edit.input` should return the expected
        command string.
        """
        edit.term.inkey.side_effect = [
            DOWN,
            SDOWN,
            LEFT,
            SLEFT,
            RIGHT,
            SRIGHT,
            UP,
            SUP,
            'x',
            ' ',
            'r',
            's',
        ]
        assert edit.input() == ('down', 1)
        assert edit.input() == ('down', 10)
        assert edit.input() == ('left', 1)
        assert edit.input() == ('left', 10)
        assert edit.input() == ('right', 1)
        assert edit.input() == ('right', 10)
        assert edit.input() == ('up', 1)
        assert edit.input() == ('up', 10)
        assert edit.input() == ('exit',)
        assert edit.input() == ('flip',)
        assert edit.input() == ('restore',)
        assert edit.input() == ('snapshot',)

    # Tests for Edit UI updates.
    def test_Edit_update_ui(self, capsys, edit, term):
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


# Tests for End.
class TestEnd:
    # Test for End initialization.
    def test_End_init(self, grid, term):
        """When given required parameters, :class:`End` should return
        an instance with attributes set to the given values.
        """
        required = {}
        obj = sui.End(**required)
        for attr in required:
            assert getattr(obj, attr) is required[attr]


# Tests for Load.
class TestLoad:
    # Fixtures for Load.
    @pt.fixture
    def load(self, grid, term):
        """A :class:`Load` object for testing."""
        load = sui.Load(grid, term)
        load.files = ['spam', 'eggs', 'ham']
        load.path = Path('tests/data')
        return load

    @pt.fixture
    def window_load(self, big_grid, small_term):
        """A :class:`Load` object for testing."""
        load = sui.Load(big_grid, small_term)
        load.files = ['spam', 'eggs', 'ham']
        load.path = Path('tests/data')
        load.origin_x = 1
        load.origin_y = 3
        return load

    # Tests for Load initialization.
    def test_Load_init(self, grid, term):
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
    def test_Load_down(self, load):
        """When called, :meth:`Load.down` should add one to
        :attr:`Load.selected`, rolling over if the number is
        above the number of files, and return the parent object.
        """
        state = load.down()
        assert state is load
        assert load.selected == 1

    def test_Load_exit(self, load):
        """When called, :meth:`Load.exit` should return a :class:`Core`
        object populated with the grid and terminal objects.
        """
        state = load.exit()
        assert isinstance(state, sui.Core)
        assert state.data == load.data
        assert state.term == load.term

    def test_Load_exit_window(self, window_load):
        """When called, :meth:`Load.exit` should return a :class:`Core`
        object populated with the grid and terminal objects.
        """
        state = window_load.exit()
        assert isinstance(state, sui.Core)
        assert state.data == window_load.data
        assert state.term == window_load.term
        assert state.origin_x == window_load.origin_x
        assert state.origin_y == window_load.origin_y

    def test_Load_file(self, load):
        """When called, :meth:`Load.file` should return a :class:`Load`
        object pointed at the current working directory.
        """
        state = load.file()
        assert isinstance(state, sui.Load)
        assert state.data is load.data
        assert state.term is load.term
        assert state.path == Path.cwd()

    def test_Load_load(self, load):
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

    def test_Load_load_directory(self, load):
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

    def test_Load_load_window(self, window_load):
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

    def test_Load_up(self, load):
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
    def test_Load_input(self, load):
        """When given input, :meth:`Load.input` should return the expected
        command string.
        """
        load.term.inkey.side_effect = [DOWN, UP, 'f', 'x', '\n',]
        assert load.input() == ('down',)
        assert load.input() == ('up',)
        assert load.input() == ('file',)
        assert load.input() == ('exit',)
        assert load.input() == ('load',)

    # Tests for Load UI updates.
    def test_Load_update_ui(self, capsys, load, term):
        """When called, :meth:`Load.update_ui` should draw the UI for
        load mode.
        """
        load.update_ui()
        captured = capsys.readouterr()
        assert repr(captured.out) == repr(
            term.move(0, 0) + term.on_green + '▸ ..'
            + term.normal + term.clear_eol + '\n'
            + term.move(1, 0) + '▸ zeggs' + term.clear_eol + '\n'
            + term.move(2, 0) + '\u2500' * 4 + '\n'
            + term.move(3, 0) + load.menu + term.clear_eol
        )

    def test_Load_update_ui_scroll_down(self, capsys, load, term):
        """When called, :meth:`Load.update_ui` should draw the UI for
        load mode. If the selected file is below the bottom of the
        displayable area, the displayed list should scroll down to
        show the selected file.
        """
        load.selected = 3
        load.update_ui()
        captured = capsys.readouterr()
        assert repr(captured.out) == repr(
            term.move(0, 0) + '.snapshot.txt' + term.clear_eol + '\n'
            + term.move(1, 0) + term.on_green + 'spam'
            + term.normal + term.clear_eol + '\n'
            + term.move(2, 0) + '\u2500' * 4 + '\n'
            + term.move(3, 0) + load.menu + term.clear_eol
        )


# Tests for Save.
class TestSave:
    # Fixtures for Save tests.
    @pt.fixture
    def save(self, grid, term, tmp_path):
        save = sui.Save(grid, term)
        save.path = tmp_path
        yield save

    @pt.fixture
    def window_save(self, big_grid, small_term, tmp_path):
        save = sui.Save(big_grid, small_term)
        save.path = tmp_path
        yield save

    # Tests for Save initialization.
    def test_Save_init_all_defaults(self, grid, term):
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

    def test_Save_init_all_optionals(self, grid, term):
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
    def test_Save_exit(self, save):
        """When called, :meth:`Save.exit` should return a :class:`Core`
        object.
        """
        state = save.exit()
        assert isinstance(state, sui.Core)
        assert state.data is save.data
        assert state.term is save.term

    def test_Save_save(self, save):
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

    def test_Save_save_window(self, window_save):
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
    def test_Save_input(self, capsys, mocker, save, term):
        """When given input, :meth:`Save.input` should return the expected
        command string.
        """
        save.term.inkey.side_effect = ['s', 'p', 'a', 'm', '\n']
        cmd = save.input()
        captured = capsys.readouterr()
        assert cmd == ('save', 'spam')
        assert repr(captured.out) == repr(
            term.move(4, 0) + '> ' + term.clear_eol
            + term.move(4, 2)
            + term.move(4, 2) + 's'
            + term.move(4, 3) + 'p'
            + term.move(4, 4) + 'a'
            + term.move(4, 5) + 'm'
        )

    def test_Save_backspace(self, capsys, mocker, save, term):
        """When given input, :meth:`Save.input` should return the expected
        command string. Backspace should delete characters.
        """
        save.term.inkey.side_effect = ['s', 'p', 'a', 'a', '\x7f', 'm', '\n']
        cmd = save.input()
        captured = capsys.readouterr()
        assert cmd == ('save', 'spam')
        assert repr(captured.out) == repr(
            term.move(4, 0) + '> ' + term.clear_eol
            + term.move(4, 2)
            + term.move(4, 2) + 's'
            + term.move(4, 3) + 'p'
            + term.move(4, 4) + 'a'
            + term.move(4, 5) + 'a'
            + term.move(4, 5) + ' '
            + term.move(4, 5) + 'm'
        )

    def test_Save_escape(self, mocker, save):
        """When given input, :meth:`Save.input` should return the expected
        command string. Escape should exit without saving.
        """
        save.term.inkey.side_effect = ['s', 'p', 'a', 'm', ESC]
        assert save.input() == ('exit',)

    def test_Save_tab(self, mocker, save):
        """When given input, :meth:`Save.input` should return the expected
        command string. Tab should complete directory names.
        """
        save.path = Path.cwd()
        save.term.inkey.side_effect = [
            't', 'e', '\t',
            's', 'p', 'a', 'm', '\n'
        ]
        assert save.input() == ('save', 'tests/spam')

    # Tests for Save UI updates.
    def test_Save_update_ui(self, capsys, mocker, save, term):
        """When called, :meth:`Save.update_ui` should redraw the UI
        for the save state.
        """
        mocker.patch('pathlib.Path.iterdir', return_value=['spam', 'eggs'])
        save.update_ui()
        captured = capsys.readouterr()
        assert repr(captured.out) == repr(
            grid_start_lines
            + term.move(2, 0) + '\u2500' * 4 + '\n'
            + term.move(3, 0) + save.menu + term.clear_eol
        )


# Tests for Start.
class TestStart:
    # Fixtures for Start.
    @pt.fixture
    def start(self, grid, term):
        """A :class:`Start` object for testing."""
        start = sui.Start(grid, term)
        return start

    @pt.fixture
    def window_start(self, big_grid, small_term):
        """A :class:`Start` object with a window for testing."""
        start = sui.Start(big_grid, small_term)
        start.origin_x = 1
        start.origin_y = 3
        return start

    # Tests for Start initialization.
    def test_Start_init_all_default(self, term):
        """Given no parameters, :class:`Start` should initialize an
        instance of itself using default attribute values.
        """
        start = sui.Start()
        assert start.data.width == term.width
        assert start.data.height == (term.height - 3) * 2
        assert start.origin_y == 0
        assert start.origin_x == 0
        assert start.pace == 0
        assert start.rule == 'B3/S23'
        assert start.wrap
        assert isinstance(start.term, blessed.Terminal)

    def test_Start_init_all_optionals(self, grid, term):
        """When given optional parameters, :class:`Start` should return
        an instance with attributes set to the given values. It should
        also initialize the cursor position.
        """
        optionals = {
            'data': grid,
            'term': term,
            'origin_x': 2,
            'origin_y': 3,
            'pace': 0.01,
            'rule': 'B36/S23',
            'wrap': False,
        }
        obj = sui.Start(**optionals)
        for attr in optionals:
            assert getattr(obj, attr) is optionals[attr]

    def test_Start_init_big_grid(self, big_grid, small_term):
        """Given a grid bigger than the terminal, :class:`Start` should
        initialize an instance of itself using the given grid. The origin
        for the window should be set to the middle of the grid.
        """
        start = sui.Start(big_grid, small_term)
        assert start.origin_y == 2
        assert start.origin_x == 2

    def test_Start_init_file(self, term):
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

    def test_Start_init_no_wrap(self, ):
        """Given wrap of `False`, :class:`Start` should generate a grid
        then set the grid's wrap to `False`.
        """
        start = sui.Start(wrap=False)
        assert not start.data.wrap

    def test_Start_init_rule(self, ):
        """Given a valid rule string, :class:`Start` should generate a grid
        then set the grid's rule to the given value.
        """
        start = sui.Start(rule='B36/S23')
        assert start.data.rule == 'B36/S23'

    # Tests for Start commands.
    def test_Start_run(self, start):
        """When called, :meth:`Start.run` should always return a
        :class:`Core` object initialized with the parent object's
        grid and term.
        """
        state = start.run()
        assert isinstance(state, sui.Core)
        assert state.data is start.data
        assert state.term is start.term

    def test_Start_run_window(self, window_start):
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
    def test_Start_input(self, capsys, start, term):
        """When valid given input, :meth:`Start.input` should return the
        expected command string.
        """
        start.term.inkey.side_effect = ' '
        captured = capsys.readouterr()
        assert start.input() == ('run',)

    # Tests for Start UI updates.
    def test_Start_update_ui(self, capsys, start, term):
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
