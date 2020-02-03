"""
test_ui
~~~~~~~

This provides the unit tests for life.ui.py.
"""
import unittest as ut
from unittest.mock import call, patch, PropertyMock

import blessed

from life import grid, ui


class TerminalControllerTestCase(ut.TestCase):
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
    
#     @patch('life.ui.Terminal')
    def test_default_grid_size(self):
        """The default grid should be as wide as the terminal an 
        three less than the height of the terminal.
        """
        exp = {
            'width': 80,
            'height': 21,
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