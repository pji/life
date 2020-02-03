"""
ui
~~

The user interface for Conway's Game of Life.
"""
from blessed import Terminal

from life.grid import Grid


class TerminalController:
    def __init__(self, term:Terminal) -> None:
        """Initialize an instance od the class.
        
        :param term: A blessed.Terminal object that runs the terminal 
            input and output.
        :return: None.
        :rtype: None.
        """
        self.term = term