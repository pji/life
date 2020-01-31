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
    
    def test_string_representation(self):
        """Grid objects should be able to produce a simple string 
        representation of themselves.
        """
        exp = ('...\n'
               '...')
        g = grid.Grid(3, 2)
        act = g.__str__()
        self.assertEqual(exp, act)