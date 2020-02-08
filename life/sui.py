"""
sui
~~

The user interface for Conway's Game of Life.
"""
from abc import ABC, abstractmethod

from blessed import Terminal

from life.grid import Grid


class State(ABC):
    """An abstract base class for UI states."""
    def __init__(self, data: Grid = None, term: Terminal = None):
        """Initialize a State object.
        
        :param data: (Optional.) The grid object for the current 
            game of life.
        :param term: (Optional.) The terminal the game of life is 
            being run in.
        """
        if not term:
            term = Terminal()
        self.term = term
        if not data:
            data = Grid(term.width, (term.height - 3) * 2)
        self.data = data


class Start(State):
    """The starting state for the UI."""