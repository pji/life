"""
test_ui
~~~~~~~

This provides the unit tests for life.ui.py.
"""
import unittest as ut
from unittest.mock import call, patch

import blessed

from life import ui


class TerminalControllerTestCase(ut.TestCase):
    def test_init(self):
        """TerminalController object should be initialized, setting 
        the objects attributes with the given values.
        """
        exp = {
            'term': blessed.Terminal,
        }
        u = ui.TerminalController(exp['term'])
        act = {
            'term': u.term,
        }
        self.assertEqual(exp, act)