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
    def test_call_with_params(self):
        """main() should accept parameters when called."""
        exp = {
            'ctlr': ui.TerminalController(),
        }
        
        # This will raise a TypeError if the class cannot accept 
        # the passed attributes.
        _ = ui.main(**exp)
    
    @patch('life.ui.TerminalController')
    def test_call_without_params(self, mock_tc):
        """main() should generate default values if parameters are 
        not passed when called.
        """
        exp = call()
        
        main = ui.main()
        next(main)
        main.close()
        act = mock_tc.mock_calls[-3]
        
        self.assertEqual(exp, act)
    
    @patch('blessed.Terminal.fullscreen')
    def test_fullscreen(self, mock_fs):
        """Iterating main() should engage fullscreen mode for the 
        terminal.
        """
        main = ui.main()
        next(main)
        mock_fs.assert_called()
    
    @patch('blessed.Terminal.hidden_cursor')
    def test_fullscreen(self, mock_hc):
        """Iterating main() should engage hidden_cursor mode for the 
        terminal.
        """
        main = ui.main()
        next(main)
        mock_hc.assert_called()


class TerminalControllerTestCase(ut.TestCase):
    # Common format templates for terminal control sequences.
    loc = '\x1b[{};{}H'

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
    
    @patch('life.ui.print')
    def test_draw(self, mock_print):
        """TerminalController.draw() should draw the user interface to 
        the termional.
        """
        exp = [
            call(self.loc.format(1, 1) + '\u2588 \u2588'),
            call(self.loc.format(2, 1) + ' \u2588 '),
            call(self.loc.format(3, 1) + '\u2588 \u2588'),
            call(self.loc.format(4, 1) + '\u2500\u2500\u2500'),
            call(self.loc.format(5, 1) + '(N)ext, (R)andom, (Q)uit'),
            call(self.loc.format(6, 1) + '> '),
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