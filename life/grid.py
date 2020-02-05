"""
grid
~~~~

A simple object for handling cells in Conway's Game of Life.
"""
from collections.abc import MutableSequence
from copy import copy
from random import choice

class Grid(MutableSequence):
    def __init__(self, width:int, height:int) -> None:
        """Initialize an instance of the class."""
        self.width = width
        self.height = height
        self._data = self._make_empty_grid(self.width, self.height)
    
    def __delitem__(self, key):
        return self._data.__delitem__(key)
    
    def __getitem__(self, key):
        return self._data.__getitem__(key)
    
    def __len__(self):
        return self._data.__len__()
    
    def __repr__(self):
        cls = self.__class__.__name__
        return f'{cls}(width={self.width}, height={self.height})'
    
    def __setitem__(self, key, value):
        return self._data.__setitem__(key, value)
    
    def __str__(self):
        rows = []
        for row in self._data:
            s = ''
            for col in row:
                if col:
                    s += 'X'
                else:
                    s += '.'
            rows.append(s)
        return '\n'.join(rows)
    
    def _make_empty_grid(self, width:int, height:int) -> list:
        """Create a blank 2D grid of the given dimensions."""
        return [[False for col in range(width)] for row in range(height)]
    
    def insert(self, i, x):
        return self._data.insert(i, x)
    
    def neighbors(self, x, y):
        """Return the coordinates of the adjacent cells."""
        mods = (-1, 0, 1)
        rows = [(x + mod) % self.height for mod in mods]
        cols = [(y + mod) % self.width for mod in mods]
        coords = []
        for row in rows:
            coords.extend((row, col) for col in cols)
        del coords[4]
        return coords
    
    def next_generation(self):
        """Calculate the next generation for the grid."""
        counts = self._make_empty_grid(self.width, self.height)
        for x in range(len(self)):
            for y in range(len(self[x])):
                if self[x][y]:
                    affected = self.neighbors(x, y)
                    for i, j in affected:
                        counts[i][j] += 1
        new = self._make_empty_grid(self.width, self.height)
        for x in range(len(self)):
            for y in range(len(self[x])):
                if self[x][y] and counts[x][y] == 2:
                    new[x][y] = True
                elif counts[x][y] == 3:
                    new[x][y] = True
        self._data = new
    
    def randomize(self):
        """Randomly set each value in the grid to True or False."""
        for i in range(self.width):
            for j in range(self.height):
                self._data[j][i] = choice([True, False])
