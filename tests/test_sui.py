"""
test_sui
~~~~~~~

This provides the unit tests for life.sui.py.
"""
import unittest as ut
from unittest.mock import call, patch, PropertyMock

import blessed
import numpy as np
import pytest as pt

from life import life
from life import sui


# Terminal colors.
BG_BLACK = 40
BG_GREEN = 42
FG_GREEN = 32
FG_BGREEN = 92
FG_BWHITE = 97

# Terminal keys:
DOWN = '\x1b[B'
UP = '\x1b[A'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'

# Terminal control sequence templates.
term_ = blessed.Terminal()
clr_eol = term_.clear_eol


class color:
    @classmethod
    def format(cls, n):
        if term_.green:
            return '\x1b[{}m'.format(n)
        return ''


class loc:
    @classmethod
    def format(cls, y, x):
        return term_.move(y - 1, x - 1)


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
def edit(grid, term):
    """An :class:`Edit` object for testing."""
    return sui.Edit(grid, term)


@pt.fixture
def snapshot():
    old_value = sui.SNAPSHOT
    sui.SNAPSHOT = 'tests/data/.snapshot.txt'
    yield sui.SNAPSHOT
    sui.SNAPSHOT = old_value


@pt.fixture
def tmpshot(tmp_path):
    """A temporary directory for the snapshot file."""
    path = tmp_path / '.snapshot.txt'
    old_value = sui.SNAPSHOT
    sui.SNAPSHOT = path
    yield path
    sui.SNAPSHOT = old_value


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


def test_Edit_restore(edit, snapshot, term):
    """When called, :meth:`Edit.restore` should load the snapshot file
    and return the parent object.
    """
    state = edit.restore()
    assert state is edit
    assert (edit.data._data == np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
    ], dtype=bool)).all()


def test_Edit_snapshot(capsys, edit, tmpshot, term):
    """When called, :meth:`Edit.snapshot` should write the grid to
    the snapshot file and return the parent object.
    """
    state = edit.snapshot()
    with open(tmpshot) as fh:
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
def test_Edit_init(grid, term):
    """When given required parameters, :class:`End` should return
    an instance with attributes set to the given values.
    """
    required = {}
    obj = sui.End(**required)
    for attr in required:
        assert getattr(obj, attr) is required[attr]


class LoadTestCase(ut.TestCase):
    def _make_load(self, height=3, width=3):
        return sui.Load(life.Grid(width, height), blessed.Terminal())

    def test_init_with_parameters(self):
        """Given grid and term, Load.__init__() will set the Load
        objects attributes with the given values.
        """
        exp = {
            'data': life.Grid(3, 3),
            'term': blessed.Terminal(),
        }
        state = sui.Load(**exp)
        act = {
            'data': state.data,
            'term': state.term,
        }
        self.assertDictEqual(exp, act)

    def test_cmd_down(self):
        """When called, Load.down() should add one to Load.selected,
        rolling over if the number is above the number of files, and
        return the Load object.
        """
        state = self._make_load()
        exp_selection = 1
        exp_return = state

        state.files = ['spam', 'eggs', 'ham']
        act_return = state.down()
        act_selection = exp_return.selected

        self.assertEqual(exp_return, act_return)
        self.assertEqual(exp_selection, act_selection)

    def test_cmd_exit(self):
        """When called, Load.exit() should return a Core object
        populated with the grid and terminal objects.
        """
        state = self._make_load()
        exp_class = sui.Core
        exp_attrs = {
            'data': state.data,
            'term': state.term,
        }

        act_obj = state.exit()
        act_attrs = {
            'data': act_obj.data,
            'term': act_obj.term,
        }

        self.assertIsInstance(act_obj, exp_class)
        self.assertDictEqual(exp_attrs, act_attrs)

    @patch('life.sui.print')
    @patch('life.life.Grid.replace')
    @patch('life.sui.open')
    def test_cmd_load(self, mock_open, mock_replace, _):
        """TerminalController.replace() should advance the generation of
        the grid and update the display.
        """
        state = self._make_load()
        exp_class = sui.Core
        exp_attrs = {
            'data': state.data,
            'term': state.term,
        }

        mock_open().__enter__().readlines.return_value = ['xoxo',]
        state.files = ['spam', 'eggs']
        act_obj = state.load()
        act_attrs = {
            'data': act_obj.data,
            'term': act_obj.term,
        }

        self.assertIsInstance(act_obj, exp_class)
        self.assertDictEqual(exp_attrs, act_attrs)
        mock_replace.assert_called_with([[True, False, True, False],])
        mock_open.assert_called_with('pattern/spam', 'r')

    def test_cmd_up(self):
        """When called, Load.up() should subtract one from
        Load.selected, rolling over if the number is below
        zero, and return the Load object.
        """
        state = self._make_load()
        exp_selection = 2
        exp_return = state

        state.files = ['spam', 'eggs', 'ham']
        act_return = state.up()
        act_selection = exp_return.selected

        self.assertEqual(exp_return, act_return)
        self.assertEqual(exp_selection, act_selection)

    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey')
    @patch('life.sui.print')
    def _get_input_response(self, sym_input, mock_print, mock_inkey, _):
        exp_calls = [
            call(loc.format(5, 1) + '' + clr_eol, end='', flush=True),
        ]

        mock_inkey.return_value = sym_input
        state = self._make_load()
        state.files = ['spam', 'eggs']
        response = state.input()
        act_calls = mock_print.mock_calls

        self.assertListEqual(exp_calls, act_calls)
        return response

    def test_input_down(self):
        """Load.input() should return the down command when the down
        arrow is pressed.
        """
        exp = ('down',)
        act = self._get_input_response(DOWN)
        self.assertTupleEqual(exp, act)

    def test_input_exit(self):
        """Load.input() should return the exit command when the exit
        arrow is pressed.
        """
        exp = ('exit',)
        act = self._get_input_response('e')
        self.assertTupleEqual(exp, act)

    def test_input_load(self):
        """Load.input() should return the load command when return is
        pressed.
        """
        exp = ('load',)
        act = self._get_input_response('\n')
        self.assertTupleEqual(exp, act)

    def test_input_up(self):
        """Load.input() should return the up command when the up arrow
        is pressed.
        """
        exp = ('up',)
        act = self._get_input_response(UP)
        self.assertTupleEqual(exp, act)

    @patch('life.sui.listdir', return_value=['spam', 'eggs'])
    @patch('life.sui.print')
    def test_update_ui(self, mock_print, _):
        """When called, Load.update_ui should update the UI for the
        load state.
        """
        exp = [
            call(loc.format(1, 1) + color.format(BG_GREEN) + 'eggs'
                 + color.format(BG_BLACK) + clr_eol),
            call(loc.format(2, 1) + 'spam' + clr_eol),
            call(loc.format(3, 1) + '\u2500' * 3),
            call(loc.format(4, 1) + '(\u2191\u2192) Move, (\u23ce) Select, '
                 + '(E)xit' + clr_eol.format(4, 10), end='', flush=True),
        ]

        state = self._make_load()
        state.update_ui()
        act = mock_print.mock_calls

        self.assertListEqual(exp, act)

    @patch('life.sui.listdir', return_value=['spam',])
    @patch('life.sui.print')
    def test_update_ui_clear_empty_lines(self, mock_print, _):
        """When called, Load.update_ui should update the UI for the
        load state.
        """
        exp = [
            call(loc.format(1, 1) + color.format(BG_GREEN) + 'spam'
                 + color.format(BG_BLACK) + clr_eol),
            call(loc.format(2, 1) + clr_eol),
            call(loc.format(3, 1) + '\u2500' * 3),
            call(loc.format(4, 1) + '(\u2191\u2192) Move, (\u23ce) Select, '
                 + '(E)xit' + clr_eol.format(4, 10), end='', flush=True),
        ]

        state = self._make_load()
        state.update_ui()
        act = mock_print.mock_calls

        self.assertListEqual(exp, act)


class mainTestCase(ut.TestCase):
    @patch('life.sui.print')
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey')
    def test_full_loop(self, mock_inkey, _, __):
        """The main() loop should start and end the game of life."""
        mock_inkey.side_effect = (' ', 'q')

        # The test fails if the input above doesn't terminate the
        # loop in main().
        sui.main()


class RuleTestCase(ut.TestCase):
    def _make_rule(self):
        return sui.Rule(life.Grid(3, 3), blessed.Terminal())

    @patch('life.sui.print')
    @patch('life.sui.input')
    def _get_input_response(self, sym_input, mock_input, __):
        state = self._make_rule()
        mock_input.return_value = sym_input
        act = state.input()
        return act

    def test__init__with_parameters(self):
        """Rule.__init__() should accept given parameters and use them
        as the initial values for the relevant attributes.
        """
        exp = {
            'data': life.Grid(3, 3),
            'term': blessed.Terminal(),
        }
        state = sui.Rule(**exp)
        act = {
            'data': state.data,
            'term': state.term,
        }
        self.assertDictEqual(exp, act)

    @patch('life.sui.print')
    def test_cmd_change(self, _):
        """When called, Rule.change() should change the rules of the
        grid and return an sui.Core object with the grid and terminal
        objects.
        """
        state = self._make_rule()
        exp_class = sui.Core
        exp_attrs = {
            'data': state.data,
            'term': state.term,
            'rule': 'B3/S23'
        }

        act_obj = state.change(exp_attrs['rule'])
        act_attrs = {
            'data': act_obj.data,
            'term': act_obj.term,
            'rule': act_obj.data.rule
        }

        self.assertIsInstance(act_obj, exp_class)
        self.assertDictEqual(exp_attrs, act_attrs)

    @patch('life.sui.print')
    def test_cmd_exit(self, _):
        """When called, Rule.exit() should return a sui.Core
        object populated with the grid and terminal objects
        without changing the rules of the grid object.
        """
        state = self._make_rule()
        exp_class = sui.Core
        exp_attrs = {
            'data': state.data,
            'term': state.term,
            'rule': state.data.rule,
        }

        act_obj = state.exit()
        act_attrs = {
            'data': act_obj.data,
            'term': act_obj.term,
            'rule': act_obj.data.rule,
        }

        self.assertIsInstance(act_obj, exp_class)
        self.assertDictEqual(exp_attrs, act_attrs)

    def test_input_change(self):
        """When given a rule, Rule.input() should return the change
        command and the given rule.
        """
        rule = 'B0/S0'
        exp = ('change', rule)
        act = self._get_input_response(rule)
        self.assertTupleEqual(exp, act)

    def test_input_exit(self):
        """When given no rule, Rule.input() should return the exit
        command.
        """
        exp = ('exit',)
        act = self._get_input_response('')
        self.assertTupleEqual(exp, act)

    @patch('life.sui.print')
    def test_update_ui(self, mock_print):
        """Rule.update_ui() should redraw the UI for the rule state."""
        state = self._make_rule()
        exp = [
            call(loc.format(1, 1) + '   '),
            call(loc.format(2, 1) + '   '),
            call(loc.format(3, 1) + '\u2500' * state.data.width),
            call(loc.format(4, 1) + state.menu + clr_eol, end='', flush=True),
        ]

        state.update_ui()
        act = mock_print.mock_calls

        self.assertListEqual(exp, act)


class SaveTestCase(ut.TestCase):
    def _make_save(self):
        return sui.Save(life.Grid(3, 3), blessed.Terminal())

    def test__init__with_parameters(self):
        """Save.__init__() should accept given parameters and use them
        as the initial values for the relevant attributes.
        """
        exp = {
            'data': life.Grid(3, 3),
            'term': blessed.Terminal(),
        }
        state = sui.Save(**exp)
        act = {
            'data': state.data,
            'term': state.term,
        }
        self.assertDictEqual(exp, act)

    @patch('life.sui.open')
    def test_cmd_save(self, mock_open):
        """Given a filename, Save.save() should save the current grid
        to a file and return a Core object.
        """
        exp_class = sui.Core
        exp_calls = [
            call('pattern/spam', 'w'),
            call().__enter__(),
            call().__enter__().write('X'),
            call().__exit__(None, None, None),
        ]

        state = self._make_save()
        state.data[1][1] = True
        act_obj = state.save('spam')
        act_calls = mock_open.mock_calls

        self.assertIsInstance(act_obj, exp_class)
        self.assertListEqual(exp_calls, act_calls)

    @patch('life.sui.input', return_value='spam.txt')
    @patch('life.sui.print')
    def test_input(self, _, __):
        """When called, Save.input() should get a file name from the
        user and return the save command with the filename.
        """
        exp = ('save', 'spam.txt')
        state = self._make_save()
        act = state.input()
        self.assertTupleEqual(exp, act)

    @patch('life.sui.listdir', return_value=['spam', 'eggs'])
    @patch('life.sui.print')
    def test_update_ui(self, mock_print, _):
        """When called, Save.update_ui should update the UI for the
        save state.
        """
        exp = [
            call(loc.format(1, 1) + 'spam' + clr_eol),
            call(loc.format(2, 1) + 'eggs' + clr_eol),
            call(loc.format(3, 1) + '\u2500' * 3),
            call(loc.format(4, 1) + 'Enter name for save file.'
                 + clr_eol.format(4, 10), end='', flush=True),
        ]

        state = self._make_save()
        state.update_ui()
        act = mock_print.mock_calls

        self.assertListEqual(exp, act)

    @patch('life.sui.listdir', return_value=['spam',])
    @patch('life.sui.print')
    def test_update_ui_clear_empty_lines(self, mock_print, _):
        """When called, Save.update_ui should update the UI for the
        save state.
        """
        exp = [
            call(loc.format(1, 1) + 'spam' + clr_eol),
            call(loc.format(2, 1) + clr_eol),
            call(loc.format(3, 1) + '\u2500' * 3),
            call(loc.format(4, 1) + 'Enter name for save file.'
                 + clr_eol.format(4, 10), end='', flush=True),
        ]

        state = self._make_save()
        state.update_ui()
        act = mock_print.mock_calls

        self.assertListEqual(exp, act)


class StartTestCase(ut.TestCase):
    def _dicteq(self, expected, actual):
        self.assertDictEqual(expected, actual)

    def _listeq(self, expected, actual):
        self.assertListEqual(expected, actual)

    def test_init_without_parameters(self):
        """Start.__init__() should create default attribute values
        if no parameters are passed to it.
        """
        exp = {
            'data': life.Grid,
            'term': blessed.Terminal,
        }
        state = sui.Start()
        act = {
            'data': type(state.data),
            'term': type(state.term),
        }
        self._dicteq(exp, act)

    def test_init_with_parameters(self):
        """Start.__init__() should set the given parameters, as
        the initial attribute values.
        """
        exp = {
            'data': life.Grid(3, 3),
            'term': blessed.Terminal(),
        }
        state = sui.Start(**exp)
        act = {
            'data': state.data,
            'term': state.term,
        }
        self._dicteq(exp, act)

    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey', return_value=' ')
    @patch('life.sui.print')
    def test_input(self, mock_print, _, __):
        """Start.input() should return the run command if any key is
        pressed."""
        term = blessed.Terminal()
        exp = ('run',)
        exp_calls = [
            call(loc.format(term.height, 1) + 'Press any key to continue.'
                 + clr_eol, end='', flush=True),
        ]

        state = sui.Start()
        act = state.input()
        act_calls = mock_print.mock_calls

        self.assertTupleEqual(exp, act)
        self.assertListEqual(exp_calls, act_calls)

    def test_run(self):
        """Start.run() should always return a Core object
        initialized with the Start object's grid and term.
        """
        exp_class = sui.Core
        exp_attrs = {
            'data': life.Grid(3, 3),
            'term': blessed.Terminal(),
        }

        state = sui.Start(**exp_attrs)
        act = state.run()
        act_attrs = {
            'data': act.data,
            'term': act.term,
        }

        self.assertIsInstance(act, exp_class)
        self.assertDictEqual(exp_attrs, act_attrs)

    @patch('life.sui.print')
    def test_update_ui(self, mock_print):
        """Start.update_ui() should draw the initial UI."""
        data = life.Grid(3, 3)
        term = blessed.Terminal()
        state = sui.Start(data, term)
        exp = [
            call(loc.format(1, 1) + '   '),
            call(loc.format(2, 1) + '   '),
            call(loc.format(3, 1) + '\u2500' * data.width),
            call(loc.format(4, 1) + state.menu + clr_eol, end='', flush=True),
        ]

        state.update_ui()
        act = mock_print.mock_calls

        self._listeq(exp, act)
