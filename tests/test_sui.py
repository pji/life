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
loc = '\x1b[{};{}H'
clr_eol = '\x1b[{};{}H\x1b[K'


# Test cases.
class CoreTestCase(ut.TestCase):
    def _make_core(self):
        return sui.Core(grid.Grid(3, 3), blessed.Terminal())
    
    def test_init_with_parameters(self):
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
            call(clr_eol.format(5, 1), end=''),
            call(loc.format(5, 1) +  '> ', end='', flush=True),
        ]
        
        mock_inkey.return_value = sym_input
        state = self._make_core()
        response = state.input()
        act_calls = mock_print.mock_calls
        
        self.assertListEqual(exp_calls, act_calls)
        return response
    
    def test_input_clear(self):
        """Core.clear() should return the clear command when selected 
        by the user.
        """
        exp = ('clear',)
        act = self._get_input_response('c')
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
    
    def test_input_quit(self):
        """Core.input() should return the quit command when selected 
        by the user.
        """
        exp = ('quit',)
        act = self._get_input_response('q')
        self.assertTupleEqual(exp, act)
    
    @patch('life.grid.Grid.clear')
    def test_cmd_clear(self, mock_clear):
        """Core.clear() should clear the grid and return the Core 
        object.
        """
        exp = self._make_core()
        act = exp.clear()
        self.assertEqual(exp, act)
        mock_clear.assert_called()
    
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
    
    @patch('life.sui.print')
    def test_update_ui(self, mock_print):
        """Core.update_ui() should redraw the UI for the core state."""
        state = self._make_core()
        exp = [
            call(loc.format(1, 1) + '   '),
            call(loc.format(2, 1) + '   '),
            call(loc.format(3, 1) + '\u2500' * state.data.width),
            call(loc.format(4, 1) + ' ' * state.term.width),
            call(loc.format(4, 1) + state.menu),
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
            call(clr_eol.format(term.height, 1), end=''),
            call(loc.format(term.height, 1) +  'Press any key to continue.', 
                 end='', flush=True),
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
            call(loc.format(4, 1) + ' ' * term.width),
            call(loc.format(4, 1) + state.menu),
        ]
        
        state.update_ui()
        act = mock_print.mock_calls
        
        self._listeq(exp, act)
    
