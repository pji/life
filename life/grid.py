"""
grid
~~~~

A simple object for handling cells in Conway's Game of Life.
"""
class Grid:
    def __init__(self, width:int, height:int) -> None:
        """Initialize an instance of the class."""
        self.width = width
        self.height = height
        self._data = self._make_empty_grid(self.width, self.height)
    
    def __repr__(self):
        cls = self.__class__.__name__
        return f'{cls}(width={self.width}, height={self.height})'
    
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