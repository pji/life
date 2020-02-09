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