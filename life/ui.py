"""
ui
~~

The user interface for Conway's Game of Life.
"""
from blessed import Terminal

from life.grid import Grid


class TerminalController:
    def __init__(self, data: Grid = None, term: Terminal = None) -> None:
        """Initialize an instance od the class.
        
        :param term: A blessed.Terminal object that runs the terminal 
            input and output.
        :return: None.
        :rtype: None.
        """
        if not term:
            term = Terminal()
        self.term = term
        if not data:
            data = Grid(term.width, term.height - 3)
        self.data = data


def main(ctlr:TerminalController = None) -> None:
    if not ctlr:
        ctlr = TerminalController()