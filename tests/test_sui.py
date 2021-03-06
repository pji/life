"""
test_sui
~~~~~~~

This provides the unit tests for life.sui.py.
"""
import unittest as ut
from unittest.mock import call, patch, PropertyMock

import blessed

from life import grid, sui


# Terminal control sequence templates.
clr_eol = '\x1b[K'
color = '\x1b[{}m'
loc = '\x1b[{};{}H'

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


# Test cases.
class AutorunTestCase(ut.TestCase):
    def _make_autorun(self):
        return sui.Autorun(grid.Grid(3, 3), blessed.Terminal())
    
    @patch('blessed.Terminal.cbreak')
    @patch('life.sui.print')
    @patch('blessed.Terminal.inkey')
    def _get_input_response(self, sym_input, mock_inkey, _, __):
        mock_inkey.return_value = sym_input
        state = self._make_autorun()
        response = state.input()
        return response
    
    def test__init__with_parameters(self):
        """Autorun.__init__() should accept given parameters and use 
        them as the initial values for the relevant attributes.
        """
        exp = {
            'data': grid.Grid(3, 3),
            'term': blessed.Terminal(),
        }
        state = sui.Autorun(**exp)
        act = {
            'data': state.data,
            'term': state.term,
        }
        self.assertDictEqual(exp, act)
    
    @patch('life.sui.print')
    def test_cmd_exit(self, _):
        """When called, Autorun.exit() should return a sui.Core 
        object populated with the grid and terminal objects.
        """
        state = self._make_autorun()
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
    @patch('life.grid.Grid.next_generation')
    def test_cmd_run(self, mock_ng, _):
        """When called, Autorun.run() should advance the grid and 
        return the Autorun object.
        """
        exp_class = sui.Autorun
        
        state = self._make_autorun()
        act_obj = state.run()
        
        self.assertIsInstance(act_obj, exp_class)
        mock_ng.assert_called()

    def test_input_exit(self):
        """If a key is pressed, Autorun.input() should return the exit 
        command.
        """
        exp = ('exit',)
        act = self._get_input_response(' ')
        self.assertTupleEqual(exp, act)
    
    def test_input_timeout(self):
        """If timed out, Autorun.input() should return the run 
        command.
        """
        exp = ('run',)
        act = self._get_input_response('')
        self.assertTupleEqual(exp, act)
    
    @patch('life.sui.print')
    def test_update_ui(self, mock_print):
        """Autorun.update_ui() should redraw the UI for the core state."""
        state = self._make_autorun()
        exp = [
            call(loc.format(1, 1) + '   '),
            call(loc.format(2, 1) + '   '),
            call(loc.format(3, 1) + '\u2500' * state.data.width),
            call(loc.format(4, 1) + state.menu + clr_eol, end='', flush=True),
        ]
        
        state.update_ui()
        act = mock_print.mock_calls
        
        self.assertListEqual(exp, act)


class CoreTestCase(ut.TestCase):
    def _make_core(self):
        return sui.Core(grid.Grid(3, 3), blessed.Terminal())
    
    def test__init__with_parameters(self):
        """Core.__init__() should accept given parameters and use them 
        as the initial values for the relevant attributes.
        """
        exp = {
            'data': grid.Grid(3, 3),
            'term': blessed.Terminal(),
        }
        state = sui.Core(**exp)
        act = {
            'data': state.data,
            'term': state.term,
        }
        self.assertDictEqual(exp, act)
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey')
    @patch('life.sui.print')
    def _get_input_response(self, sym_input, mock_print, mock_inkey, _):
        exp_calls = [
            call(loc.format(5, 1) +  '' + clr_eol, end='', flush=True),
        ]
        
        mock_inkey.return_value = sym_input
        state = self._make_core()
        response = state.input()
        act_calls = mock_print.mock_calls
        
        self.assertListEqual(exp_calls, act_calls)
        return response
    
    def test_input_autorun(self):
        """Core.input() should return the autorun command when 
        selected by the user.
        """
        exp = ('autorun',)
        act = self._get_input_response('a')
        self.assertTupleEqual(exp, act)
    
    def test_input_clear(self):
        """Core.input() should return the clear command when selected 
        by the user.
        """
        exp = ('clear',)
        act = self._get_input_response('c')
        self.assertTupleEqual(exp, act)
    
    def test_input_edit(self):
        """Core.input() should return the edit command when selected 
        by the user.
        """
        exp = ('edit',)
        act = self._get_input_response('e')
        self.assertTupleEqual(exp, act)
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey', side_effect=['bad', 'c'])
    @patch('life.sui.print')
    def test_input_invalid(self, mock_print, _, __):
        """When given an invalid input, Core.input should alert the 
        user and let them try again.
        """
        exp_calls = [
            call(loc.format(5, 1) +  '' + clr_eol, end='', flush=True),
            call(loc.format(5, 1) +  '' + clr_eol, end='', flush=True),
            call(loc.format(5, 1) +  'Invalid command. Please try again.' 
                 + clr_eol, end='', flush=True),
        ]
        exp_return = ('clear',)
        
        state = self._make_core()
        act_return = state.input()
        act_calls = mock_print.mock_calls
        
        self.assertListEqual(exp_calls, act_calls)
        self.assertTupleEqual(exp_return, act_return)
    
    def test_input_load(self):
        """Core.input() should return the load command when selected 
        by the user.
        """
        exp = ('load',)
        act = self._get_input_response('l')
        self.assertTupleEqual(exp, act)
    
    def test_input_next(self):
        """Core.next() should return the next command when selected 
        by the user.
        """
        exp = ('next',)
        act = self._get_input_response('n')
        self.assertTupleEqual(exp, act)
    
    def test_input_random(self):
        """Core.random() should return the random command when 
        selected by the user.
        """
        exp = ('random',)
        act = self._get_input_response('r')
        self.assertTupleEqual(exp, act)
    
    def test_input_rule(self):
        exp = ('rule',)
        act = self._get_input_response('u')
        self.assertTupleEqual(exp, act)
    
    def test_input_save(self):
        exp = ('save',)
        act = self._get_input_response('s')
        self.assertTupleEqual(exp, act)
    
    def test_input_quit(self):
        """Core.input() should return the quit command when selected 
        by the user.
        """
        exp = ('quit',)
        act = self._get_input_response('q')
        self.assertTupleEqual(exp, act)
    
    def test_cmd_autorun(self):
        """Core.autorun() should return an Autorun object."""
        exp = sui.Autorun
        state = self._make_core()
        act = state.autorun()
        self.assertIsInstance(act, exp)
    
    @patch('life.grid.Grid.clear')
    def test_cmd_clear(self, mock_clear):
        """Core.clear() should clear the grid and return the Core 
        object.
        """
        exp = self._make_core()
        act = exp.clear()
        self.assertEqual(exp, act)
        mock_clear.assert_called()
    
    def test_cmd_edit(self):
        """Core.load() should return an Edit object."""
        exp = sui.Edit
        state = self._make_core()
        act = state.edit()
        self.assertIsInstance(act, exp)
    
    def test_cmd_load(self):
        """Core.load() should return an Load object."""
        exp = sui.Load
        state = self._make_core()
        act = state.load()
        self.assertIsInstance(act, exp)
    
    @patch('life.grid.Grid.next_generation')
    def test_cmd_next(self, mock_next):
        """Core.next() should advance the grid to the next generation 
        and return the Core object.
        """
        exp = self._make_core()
        act = exp.next()
        self.assertEqual(exp, act)
        mock_next.assert_called()
    
    def test_cmd_quit(self):
        """Core.quit() should return an End object."""
        exp = sui.End
        state = self._make_core()
        act = state.quit()
        self.assertIsInstance(act, exp)
    
    @patch('life.grid.Grid.randomize')
    def test_cmd_random(self, mock_random):
        """Core.random() should randomize the values of cells in the 
        grid and return the Core object.
        """
        exp = self._make_core()
        act = exp.random()
        self.assertEqual(exp, act)
        mock_random.assert_called()
    
    def test_cmd_rule(self):
        """When called, Core.rule() should return a Rule object."""
        exp = sui.Rule
        state = self._make_core()
        act = state.rule()
        self.assertIsInstance(act, exp)
    
    def test_cmd_save(self):
        """When called, Core.save() should return a Save object."""
        exp = sui.Save
        state = self._make_core()
        act = state.save()
        self.assertIsInstance(act, exp)
    
    @patch('life.sui.print')
    def test_update_ui(self, mock_print):
        """Core.update_ui() should redraw the UI for the core state."""
        state = self._make_core()
        exp = [
            call(loc.format(1, 1) + '   '),
            call(loc.format(2, 1) + '   '),
            call(loc.format(3, 1) + '\u2500' * state.data.width),
            call(loc.format(4, 1) + state.menu + clr_eol, end='', flush=True),
        ]
        
        state.update_ui()
        act = mock_print.mock_calls
        
        self.assertListEqual(exp, act)


class EditTestCase(ut.TestCase):
    def _make_edit(self):
        return sui.Edit(grid.Grid(3, 3), blessed.Terminal())
    
    @patch('life.sui.print')
    def _cmd_tests(self, exp_call, exp_row, exp_col, cmd, mock_print):
        state = self._make_edit()
        exp_return = state
        exp_calls = [
            call(loc.format(1, 1) + '   '),
            call(loc.format(2, 1) + '   '),
            exp_call,
        ]
        
        act_return = getattr(state, cmd)()
        act_row = state.row
        act_col = state.col
        act_calls = mock_print.mock_calls
        
        self.assertEqual(exp_return, act_return)
        self.assertEqual(exp_row, act_row)
        self.assertEqual(exp_col, act_col)
        self.assertListEqual(exp_calls, act_calls)
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey')
    @patch('life.sui.print')
    def _get_input_response(self, sym_input, mock_print, mock_inkey, _):
        exp_calls = [
            call(loc.format(5, 1) +  '' + clr_eol, end='', flush=True),
        ]
        
        mock_inkey.return_value = sym_input
        state = self._make_edit()
        response = state.input()
        act_calls = mock_print.mock_calls
        
        self.assertListEqual(exp_calls, act_calls)
        return response
    
    def test__init__with_parameters(self):
        """Given grid and term, Edit.__init__() will set the Edit 
        objects attributes with the given values.
        """
        exp = {
            'data': grid.Grid(3, 3),
            'term': blessed.Terminal(),
        }
        state = sui.Edit(**exp)
        act = {
            'data': state.data,
            'term': state.term,
        }
        self.assertDictEqual(exp, act)
    
    def test_cmd_down(self):
        """When called, Edit.down() should subtract one from the row, 
        redraw the status, redraw the cursor, and return the Edit 
        state.
        """
        exp_call = call(loc.format(2, 2) + color.format(FG_GREEN) + '\u2580' 
                        + color.format(FG_BWHITE) + color.format(BG_BLACK))
        exp_row = 2
        exp_col = 1
        cmd = 'down'
        self._cmd_tests(exp_call, exp_row, exp_col, cmd)
    
    def test_cmd_exit(self):
        """When called, Edit.exit should return a Core object."""
        state = self._make_edit()
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
    def test_cmd_flip(self, mock_print):
        """When called, Edit.flip() should pass the current coordinates 
        to Grid.flip(), redraw the status and cursor,  and return the 
        Edit object.
        """
        state = self._make_edit()
        exp_return = state
        exp_row = 1
        exp_col = 1
        exp_calls = [
            call(loc.format(1, 1) + ' \u2584 '),
            call(loc.format(2, 1) + '   '),
            call(loc.format(1, 2) + color.format(FG_BGREEN) + '\u2584' 
                 + color.format(FG_BWHITE) + color.format(BG_BLACK)),
        ]
        
        act_return = state.flip()
        act_row = state.row
        act_col = state.col
        act_calls = mock_print.mock_calls
        
        self.assertEqual(exp_return, act_return)
        self.assertEqual(exp_row, act_row)
        self.assertEqual(exp_col, act_col)
        self.assertListEqual(exp_calls, act_calls)
    
    def test_cmd_left(self):
        """When called, Edit.left() should subtract one from the col, 
        redraw the status, redraw the cursor, and return the Edit 
        state.
        """
        exp_call = call(loc.format(1, 1) + color.format(FG_GREEN) + '\u2584' 
                        + color.format(FG_BWHITE) + color.format(BG_BLACK))
        exp_row = 1
        exp_col = 0
        cmd = 'left'
        self._cmd_tests(exp_call, exp_row, exp_col, cmd)
    
    def test_cmd_right(self):
        """When called, Edit.right() should add one from the col, 
        redraw the status, redraw the cursor, and return the Edit 
        state.
        """
        exp_call = call(loc.format(1, 3) + color.format(FG_GREEN) + '\u2584' 
                        + color.format(FG_BWHITE) + color.format(BG_BLACK))
        exp_row = 1
        exp_col = 2
        cmd = 'right'
        self._cmd_tests(exp_call, exp_row, exp_col, cmd)
    
    @patch('life.sui.print')
    @patch('life.grid.Grid.replace')
    @patch('life.sui.open')
    def test_cmd_restore(self, mock_open, mock_replace, _):
        """When called, Edit.restore() should load the snapshot file 
        and return the Edit object.
        """
        state = self._make_edit()
        exp_class = sui.Edit
        exp_attrs = {
            'data': state.data,
            'term': state.term,
        }
        
        mock_open().__enter__().readlines.return_value = ['xoxo',]
        act_obj = state.restore()
        act_attrs = {
            'data': act_obj.data,
            'term': act_obj.term,
        }
        
        self.assertIsInstance(act_obj, exp_class)
        self.assertDictEqual(exp_attrs, act_attrs)
        mock_replace.assert_called_with([[True, False, True, False],])
        mock_open.assert_called_with('pattern/.snapshot.txt', 'r')
    
    @patch('life.sui.print')
    @patch('life.sui.open')
    def test_cmd_snapshot(self, mock_open, _):
        """When called, Edit.snapshot() should write the grid to 
        the snapshot file and return the Edit object.
        """
        exp_class = sui.Edit
        exp_calls = [
            call('pattern/.snapshot.txt', 'w'),
            call().__enter__(),
            call().__enter__().write('X'),
            call().__exit__(None, None, None),
        ]
        
        state = self._make_edit()
        state.data[1][1] = True
        act_obj = state.snapshot()
        act_calls = mock_open.mock_calls
        
        self.assertIsInstance(act_obj, exp_class)
        self.assertListEqual(exp_calls, act_calls)
    
    def test_cmd_up(self):
        """When called, Edit.up() should subtract one from the row, 
        redraw the status, redraw the cursor, and return the Edit 
        state.
        """
        exp_call = call(loc.format(1, 2) + color.format(FG_GREEN) + '\u2580' 
                        + color.format(FG_BWHITE) + color.format(BG_BLACK))
        exp_row = 0
        exp_col = 1
        cmd = 'up'
        self._cmd_tests(exp_call, exp_row, exp_col, cmd)
    
    def test_input_down(self):
        """Edit.input() should return the down command when the down 
        key is pressed.
        """
        exp = ('down',)
        act = self._get_input_response(DOWN)
        self.assertTupleEqual(exp, act)
    
    def test_input_exit(self):
        """Edit.input() should return the exit command when the 'e' 
        key is pressed.
        """
        exp = ('exit',)
        act = self._get_input_response('e')
        self.assertTupleEqual(exp, act)
    
    def test_input_flip(self):
        """Edit.input() should return the flip command when the space 
        bar is pressed.
        """
        exp = ('flip',)
        act = self._get_input_response(' ')
        self.assertTupleEqual(exp, act)
    
    def test_input_left(self):
        """Edit.input() should return the left command when the left 
        key is pressed.
        """
        exp = ('left',)
        act = self._get_input_response(LEFT)
        self.assertTupleEqual(exp, act)
    
    def test_input_restore(self):
        """Edit.restore() should return the restore command when the 
        r key is pressed.
        """
        exp = ('restore',)
        act = self._get_input_response('r')
        self.assertTupleEqual(exp, act)
    
    def test_input_right(self):
        """Edit.input() should return the right command when the right 
        key is pressed.
        """
        exp = ('right',)
        act = self._get_input_response(RIGHT)
        self.assertTupleEqual(exp, act)
    
    def test_input_snapshot(self):
        """Edit.snapshot() should return the snapshot command when the 
        s key is pressed.
        """
        exp = ('snapshot',)
        act = self._get_input_response('s')
        self.assertTupleEqual(exp, act)
    
    def test_input_up(self):
        """Edit.input() should return the up command when the up 
        key is pressed.
        """
        exp = ('up',)
        act = self._get_input_response(UP)
        self.assertTupleEqual(exp, act)
    
    @patch('life.sui.print')
    def test_update_ui(self, mock_print):
        """When called, Edit.update_ui should draw the UI for edit 
        mode.
        """
        state = self._make_edit()
        exp = [
            call(loc.format(1, 1) + '   '),
            call(loc.format(2, 1) + '   '),
            call(loc.format(3, 1) + '\u2500' * state.data.width),
            call(loc.format(4, 1) + state.menu + clr_eol, end='', flush=True),
            call(loc.format(1, 2) + color.format(FG_GREEN) + '\u2584' 
                 + color.format(FG_BWHITE) + color.format(BG_BLACK)),
        ]
        
        state.update_ui()
        act = mock_print.mock_calls
        
        self.assertListEqual(exp, act)


class EndTestCase(ut.TestCase):
    def test_init_without_parameters(self):
        """End.__init__() should not require parameters."""
        exp = sui.End
        act = exp()
        self.assertIsInstance(act, exp)


class LoadTestCase(ut.TestCase):
    def _make_load(self, height=3, width=3):
        return sui.Load(grid.Grid(width, height), blessed.Terminal())
    
    def test_init_with_parameters(self):
        """Given grid and term, Load.__init__() will set the Load 
        objects attributes with the given values.
        """
        exp = {
            'data': grid.Grid(3, 3),
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
    @patch('life.grid.Grid.replace')
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
            call(loc.format(5, 1) +  '' + clr_eol, end='', flush=True),
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
        return sui.Rule(grid.Grid(3, 3), blessed.Terminal())
    
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
            'data': grid.Grid(3, 3),
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
        return sui.Save(grid.Grid(3, 3), blessed.Terminal())
    
    def test__init__with_parameters(self):
        """Save.__init__() should accept given parameters and use them 
        as the initial values for the relevant attributes.
        """
        exp = {
            'data': grid.Grid(3, 3),
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
            'data': grid.Grid,
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
            'data': grid.Grid(3, 3),
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
            call(loc.format(term.height, 1) +  'Press any key to continue.' 
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
            'data': grid.Grid(3, 3),
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
        data = grid.Grid(3, 3)
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
    
