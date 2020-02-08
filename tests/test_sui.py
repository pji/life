"""
test_sui
~~~~~~~

This provides the unit tests for life.sui.py.
"""
import unittest as ut
from unittest.mock import call, patch, PropertyMock

import blessed

from life import grid, sui


class StartTestCase(ut.TestCase):
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
        self.assertDictEqual(exp, act)