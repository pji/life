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
    def _get_input_response(self, sym_input, mock_inkey, _):
        mock_inkey.return_value = sym_input
        state = self._make_core()
        return state.input()
    
    def test_input_quit(self):
        """Core.input() should return the quit command when selected 
        by the user.
        """
        exp = ('quit',)
        act = self._get_input_response('q')
        self.assertTupleEqual(exp, act)
    
    def test_quit(self):
        """Core.quit() should return an End object."""
        exp = sui.End
        state = self._make_core()
        act = state.quit()
        self.assertIsInstance(act, exp)


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
    def test_input(self, _, __):
        """Start.input() should return the run command if any key is 
        pressed."""
        exp = ('run',)
        state = sui.Start()
        act = state.input()
        self.assertTupleEqual(exp, act)
        
    
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
            call(loc.format(5, 1) + state.prompt, end=''),
        ]
        
        state.update_ui()
        act = mock_print.mock_calls
        
        self._listeq(exp, act)
    
