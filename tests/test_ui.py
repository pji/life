"""
test_ui
~~~~~~~

This provides the unit tests for life.ui.py.
"""
import unittest as ut
from unittest.mock import call, patch, PropertyMock

import blessed

from life import grid, ui


class mainTestCase(ut.TestCase):
    @patch('life.ui.print')
    @patch('life.ui.TerminalController.input', return_value=ui._Command('q'))
    def test_call_with_params(self, mock_input, _):
        """main() should accept parameters when called."""
        exp = {
            'ctlr': ui.TerminalController(),
        }
                
        # This will raise a TypeError if the class cannot accept 
        # the passed attributes.
        _ = ui.main(**exp)
    
    @patch('life.ui.print')
    @patch('life.ui.TerminalController')
    def test_call_without_params(self, mock_tc, _):
        """main() should generate default values if parameters are 
        not passed when called.
        """
        exp = call()
        
        mock_tc().input.return_value = ui._Command('q')
        ui.main()
        act = mock_tc.mock_calls[-3]
        
        self.assertEqual(exp, act)
    
    @patch('blessed.Terminal.inkey', return_value='n')
    @patch('life.ui.print')
    @patch('life.ui.TerminalController.input', return_value=ui._Command('q'))
    @patch('blessed.Terminal.fullscreen')
    def test_fullscreen(self, mock_fs, _, __, ___):
        """Iterating main() should engage fullscreen mode for the 
        terminal.
        """
        ui.main()
        mock_fs.assert_called()
    
    @patch('blessed.Terminal.inkey', return_value='n')
    @patch('life.ui.print')
    @patch('life.ui.TerminalController.input', return_value=ui._Command('q'))
    @patch('blessed.Terminal.hidden_cursor')
    def test_hidden_cursor(self, mock_hc, _, __, ___):
        """Iterating main() should engage hidden_cursor mode for the 
        terminal.
        """
        ui.main()
        mock_hc.assert_called()
    
    @patch('life.ui.print')
    @patch('life.ui.TerminalController.input', return_value=ui._Command('q'))
    def test_loop_input(self, mock_input, _):
        """Iterating main() should prompt for input."""
        ui.main()
        mock_input.assert_called()


class TerminalControllerTestCase(ut.TestCase):
    # Common format templates for terminal control sequences.
    loc = '\x1b[{};{}H'
    color = '\x1b[{}m\x1b[{}m'

    def test_init(self):
        """TerminalController object should be initialized, setting 
        the objects attributes with the given values.
        """
        exp = {
            'data': grid.Grid(5, 5),
            'term': blessed.Terminal(),
        }
        u = ui.TerminalController(**exp)
        act = {
            'data': u.data,
            'term': u.term,
        }
        self.assertEqual(exp, act)
    
    def test_init_defaults(self):
        """If no parameters are passed, Terminalcontroller should 
        create default objects for its attributes.
        """
        exp = {
            'data': grid.Grid,
            'term': blessed.Terminal,
        }
        u = ui.TerminalController()
        act = {
            'data': type(u.data),
            'term': type(u.term),
        }
        self.assertEqual(exp, act)
    
    def test_default_grid_size(self):
        """The default grid should be as wide as the terminal an 
        three less than the height of the terminal.
        """
        exp = {
            'width': 80,
            'height': 42,
        }
        
        with patch('life.ui.Terminal.width', new_callable=PropertyMock) as mock_width, \
             patch('life.ui.Terminal.height', new_callable=PropertyMock) as mock_height:
            mock_width.return_value = 80
            mock_height.return_value = 24
            u = ui.TerminalController()
            act = {
                'width': u.data.width,
                'height': u.data.height,
            }
        self.assertEqual(exp, act)
    
    @patch('life.ui.TerminalController.draw')
    @patch('life.grid.Grid.clear')
    def test_clear(self, mock_clear, mock_draw):
        """TerminalController.clear() should clear the grid."""
        tc = ui.TerminalController()
        tc.clear()
        mock_clear.assert_called()
        mock_draw.assert_called()
    
    @patch('life.ui.print')
    def test_draw(self, mock_print):
        """TerminalController.draw() should draw the user interface to 
        the termional.
        """
        term = blessed.Terminal()
        exp = [
            call(self.loc.format(1, 1) + '\u2580\u2584\u2580'),
            call(self.loc.format(2, 1) + '\u2580 \u2580'),
            call(self.loc.format(3, 1) + '\u2500\u2500\u2500'),
            call(self.loc.format(4, 1) + ' ' * term.width),
            call(self.loc.format(4, 1) + '(C)lear, (E)dit, (L)oad, (N)ext, (Q)uit, (R)andom'),
        ]
        
        g = grid.Grid(3, 3)
        data = [
            [True, False, True],
            [False, True, False],
            [True, False, True],
        ]
        g._data = data
        tc = ui.TerminalController(g)
        tc.draw()
        act = mock_print.mock_calls
        
        self.assertListEqual(exp, act)
    
    @patch('blessed.Terminal.inkey', return_value='n')
    @patch('life.ui.print')
    def test_input_valid(self, mock_print, mock_inkey):
        """When called, TerminalController.input() should write the 
        prompt to the UI and return a valid response from the user.
        """
        exp_call = call(self.loc.format(5, 1) + '> ', end='')
        exp_return = ui._Command('n')
        
        g = grid.Grid(3, 3)
        tc = ui.TerminalController(g)
        act_return = tc.input()
        act_call = mock_print.mock_calls[-1]
        
        self.assertEqual(exp_call, act_call)
        self.assertEqual(exp_return, act_return)
    
    @patch('life.ui.TerminalController.draw')
    @patch('life.grid.Grid.next_generation')
    def test_next(self, mock_ng, mock_draw):
        """TerminalController.next() should advance the generation of 
        the grid and update the display.
        """
        tc = ui.TerminalController()
        tc.next()
        mock_ng.assert_called()
        mock_draw.assert_called()
    
    @patch('life.ui.TerminalController.draw')
    @patch('life.grid.Grid.randomize')
    def test_random(self, mock_random, mock_draw):
        """TerminalController.next() should advance the generation of 
        the grid and update the display.
        """
        tc = ui.TerminalController()
        tc.random()
        mock_random.assert_called()
        mock_draw.assert_called()
    
    @patch('life.ui.exists', return_value='True')
    @patch('life.ui.isfile', return_value='True')
    @patch('life.ui.print')
    @patch('life.ui.input', return_value='spam')
    @patch('life.ui.TerminalController.draw')
    @patch('life.grid.Grid.replace')
    @patch('life.ui.open')
    def test_load(self, mock_open, mock_replace, mock_draw, _, __, ___, ____):
        """TerminalController.replace() should advance the generation of 
        the grid and update the display.
        """
        mock_open().__enter__().readlines.return_value = ['xoxo',]
        tc = ui.TerminalController()
        tc.load()
        mock_replace.assert_called_with([[True, False, True, False],])
        mock_open.assert_called_with('pattern/spam', 'r')
        mock_draw.assert_called()
    
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey', return_value='e')
    @patch('life.ui.print')
    def test_edit_commands(self, mock_print, _, __x):
        """TerminalController.edit() should replace the display mode 
        commands with its commands.
        """
        exp = call(self.loc.format(4, 1) + '(a) Left, (d) Right, '
                   '(w) Up, (s) Down, (\u2420) Flip, (E)xit')
        
        g = grid.Grid(3, 3)
        tc = ui.TerminalController(g)
        tc.edit()
        act = mock_print.mock_calls[1]
        
        self.assertEqual(exp, act)
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey', return_value='e')
    @patch('life.ui.TerminalController.draw')
    @patch('life.ui.print')
    def test_edit_exit(self, mock_print, mock_draw, _, __):
        """TerminalController.edit() should exit when the e key 
        is pressed.
        """
        g = grid.Grid(3, 3)
        tc = ui.TerminalController(g)
        tc.edit()
        mock_draw.assert_called()
        
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey', return_value='e')
    @patch('life.ui.print')
    def test_edit_initial_cursor(self, mock_print, _, __):
        """TerminalController.edit() should exit when the e key 
        is pressed.
        """
        exp = call(self.loc.format(1, 2) + self.color.format(32, 40) + 
                   '\u2584' + self.color.format(97, 40))
        
        g = grid.Grid(3, 3)
        tc = ui.TerminalController(g)
        tc.edit()
        
        # The last thing TerminalContoller.edit() does before exiting 
        # is set the command list back to display mode.
        act = mock_print.mock_calls[2]
        
        self.assertEqual(exp, act)
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey', side_effect=['a','e'])
    @patch('life.ui.print')
    def test_edit_move_cursor_left(self, mock_print, _, __):
        """TerminalController.edit() should exit when the e key 
        is pressed.
        """
        exp = call(self.loc.format(1, 1) + self.color.format(32, 40) + 
                   '\u2584' + self.color.format(97, 40))
        
        g = grid.Grid(3, 3)
        tc = ui.TerminalController(g)
        tc.edit()
        
        # The last thing TerminalContoller.edit() does before exiting 
        # is set the command list back to display mode.
        act = mock_print.mock_calls[5]
        
        self.assertEqual(exp, act)
    
    @patch('blessed.Terminal.cbreak')
    @patch('blessed.Terminal.inkey', side_effect=[' ', 'e'])
    @patch('life.ui.print')
    def test_edit_move_cursor_left(self, mock_print, _, __):
        """TerminalController.edit() should exit when the e key 
        is pressed.
        """
        exp = [
            [False, False, False],
            [False, True, False],
            [False, False, False],
        ]
        
        g = grid.Grid(3, 3)
        tc = ui.TerminalController(g)
        tc.edit()
        act = g._data
        
        self.assertEqual(exp, act)
