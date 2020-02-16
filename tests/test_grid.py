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
    
    def test_clear(self):
        """Grid.clear() should set every cell of the Grid object to 
        False.
        """
        exp = [
            [False, False, False,],
            [False, False, False,],
            [False, False, False,],
            [False, False, False,],
        ]
        
        g = grid.Grid(3, 4)
        data = [
            [True, False, True,],
            [False, True, False,],
            [True, False, True,],
            [False, False, False,],
        ]
        g._data = data
        g.clear()
        act = g._data
        
        self.assertEqual(exp, act)
    
    def test_flip(self):
        """Flip the value of the cell at the given coordinates."""
        exp = [
            [False, False, False,],
            [False, False, False,],
            [False, True, False,],
            [False, False, False,],
        ]
        
        g = grid.Grid(3, 4)
        g.flip(2, 1)
        act = g._data
        
        self.assertEqual(exp, act)
    
    def test_replace_grid(self):
        """Given a list of lists that contain True or False, 
        Grid.replace() should clear its data then place those 
        True/False values centered in its data.
        """
        exp = [
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
        ]
        
        g = grid.Grid(5, 5)
        g._data = [
            [True, False, True, False, True],
            [False, False, False, False, False],
            [False, False, True, False, False],
            [False, False, False, False, False],
            [True, False, True, False, True],
        ]
        test = [
            [True, False, True],
            [False, False, False],
            [True, False, True],
        ]
        g.replace(test)
        act = g._data
        
        self.assertListEqual(exp, act)
    
    def _replace_tests(self, exp, test, height=5, width=5):
        g = grid.Grid(width, height)
        g.replace(test)
        act = g._data
        self.assertListEqual(exp, act)
    
    def test_replace_grid_with_uneven_lines(self):
        """If the lists given have different widths, Grid.replace() 
        will add enough Falses to the end of the shorter lines until 
        all lists have the same width.
        """
        exp = [ 
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
        ]
        test = [
            [False,],
            [False, True, False, True,],
            [False, False,],
            [False, True, False, True, False],
            [False, False, False],
        ]
        self._replace_tests(exp, test)
    
    def test_replace_grid_wider_than_grid_size(self):
        """If the given grid is wider than the dimensions of the 
        current grid, Grid.replace() should use a section of the 
        given grid equal to the size of the current grid.
        """
        exp = [
            [False, False, False,],
            [True, False, True,],
            [False, False, False,],
            [True, False, True,],
            [False, False, False,],
        ]
        test = [ 
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
        ]
        self._replace_tests(exp, test, 5, 3)
    
    def test_replace_grid_taller_than_grid_size(self):
        """If the given grid is taller than the dimensions of the 
        current grid, Grid.replace() should use a section of the 
        given grid equal to the size of the current grid.
        """
        exp = [
            [False, True, False, True, False],
            [False, False, False, False, False],
            [False, True, False, True, False],
        ]
        test = [ 
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, False, False, False],
        ]
        self._replace_tests(exp, test, 3, 5)
    
    def test_highlife_replicator_t2(self):
        """Grid.next_generation should properly determine the second 
        generation of a replicator when using Highife rules.
        """
        def pat_to_grid(pat):
            return [[True if c == 'X' else False for c in row] for row in pat]
        
        before = [
            '........X.......',
            '.......X..X.....',
            '........XXXX....',
            '........XXXXX...',
            '....X..X..XX....',
            '...X.XX...XX.X..',
            '.....XX..X..X...',
            '....XXXXX.......',
            '.....XXXX.......',
            '......X..X......',
            '........X.......',
            '................',
            '................',
            '................',
            '................',
            '................',
        ]
        after = [
            '................',
            '.......X..XX....',
            '.......X....X...',
            '.......X....X...',
            '....XXXXX.......',
            '.......X.X......',
            '........XXXXX...',
            '....X....X......',
            '....X....X......',
            '.....XX..X......',
            '................',
            '................',
            '................',
            '................',
            '................',
            '................',
        ]
        
        exp = pat_to_grid(after)

        g = grid.Grid(16, 16, 'b36/s23')
        g._data = pat_to_grid(before)
        g.next_generation()
        act = g._data
        
        self.assertListEqual(exp, act)
