"""
test_grid
~~~~~~~~~

This provides the unit tests for life.grid.py.
"""
import unittest as ut
from unittest.mock import call, patch

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
    
    def test_grid_can_be_changed_by_coordinates(self):
        """The value of a given cell, addressed by indices, can be 
        changed.
        """
        exp = [
            [False, True, False],
            [False, False, False],
        ]
        g = grid.Grid(3, 2)
        g[0][1] = True
        act = g._data
        self.assertEqual(exp, act)
    
    def test_return_neighbors(self):
        """Given the coordinates of a cell, grid.neighbors() should 
        return the coordinates of its neighbors.
        """
        exp = [
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 0),
            (2, 2),
            (3, 0),
            (3, 1),
            (3, 2),
        ]
        g = grid.Grid(4, 4)
        act = g.neighbors(2, 1)
        self.assertEqual(exp, act)
    
    def test_return_neighbors_at_edge(self):
        """Given the coordinates of a cell, grid.neighbors() should 
        return the coordinates of its neighbors.
        """
        exp = [
            (3, 3),
            (3, 0),
            (3, 1),
            (0, 3),
            (0, 1),
            (1, 3),
            (1, 0),
            (1, 1),
        ]
        g = grid.Grid(4, 4)
        act = g.neighbors(0, 0)
        self.assertEqual(exp, act)
    
    def test_calculate_next_generation(self):
        """grid.next_generation() should return update itself to the 
        next generation.
        """
        exp = [
            [False, True, False, False, False,],
            [False, True, True, False, False,],
            [True, False, True, False, False,],
            [False, False, False, False, False,],
            [False, False, False, False, False,],
        ]
        
        data = [
            [False, False, False, False, False,],
            [True, True, True, False, False,],
            [False, False, True, False, False,],
            [False, True, False, False, False,],
            [False, False, False, False, False,],
        ]
        g = grid.Grid(5, 5)
        g._data = data
        g.next_generation()
        act = g._data
        
        self.assertEqual(exp, act)
    
    @patch('life.grid.choice', return_value=True)
    def test_randomize_grid(self, mock_choice):
        """Grid.randomize() should randomly set each cell in the grid 
        object to either True or False.
        """
        exp_calls = [call([True, False]) for _ in range(5 * 5)]
        exp_result = [[True for _ in range(5)] for _ in range(5)]
        g = grid.Grid(5, 5)
        g.randomize()
        act_calls = mock_choice.mock_calls
        act_result = g._data
        self.assertListEqual(exp_calls, act_calls)
        self.assertListEqual(exp_result, act_result)