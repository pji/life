"""
test_grid
~~~~~~~~~

This provides the unit tests for life.grid.py.
"""
import unittest as ut

from life import grid


class GridTestCase(ut.TestCase):
    def test_initialization(self):
        """When initialized with width and length, the Grid object 
        should store a container of bools of those dimensions.
        """
        exp = [
            [False, False, False],
            [False, False, False],
        ]
        g = grid.Grid(3, 2)
        act = g._data
        self.assertEqual(exp, act)