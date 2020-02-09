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
    
    def _char_for_state(self, top, bottom):
        """Return the character to draw based on the state of the cell."""
        if top and bottom:
            return '\u2588'
        if top and not bottom:
            return '\u2580'
        if not top and bottom:
            return '\u2584'
        if not top and not bottom:
            return ' '
    
    def _draw_commands(self, cmds: str = None):
        """Draw the available commands."""
        if not cmds:
            cmds = _Command.get_commands()
        y = -(self.data.height // -2) + 1
        print(self.term.move(y, 0) + ' ' * self.term.width)
        print(self.term.move(y, 0) + cmds)
    
    def _draw_state(self):
        """Draw the grid to the terminal."""
        data = self.data[:]
        if len(data) % 2:
            data.append([False for _ in range(len(data[0]))])
        for i in range(0, len(data), 2):
            cells = []
            for j in range(0, len(data[i])):
                char = self._char_for_state(data[i][j], data[i+1][j])
                cells.append(char)
            print(self.term.move(i // 2, 0) + ''.join(cells))
    
    def _draw_prompt(self, msg: str = '> '):
        """Draw the command prompt."""
        y = -(self.data.height // -2) + 2
        print(self.term.move(y, 0) + msg, end='')
    
    def _draw_rule(self):
        """Draw the a horizontal rule."""
        width = self.data.width
        y = -(self.data.height // -2)
        print(self.term.move(y, 0) + '\u2500' * width)
    
    @abstractmethod
    def update_ui(self):
        """Update the terminal display."""


class Start(State):
    """The starting state for the UI."""
    menu = 'Copyright © 2020 Paul J. Iutzi'
    prompt = 'Press any key to continue.'
    
    def update_ui(self):
        """Draw the initial display state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)
        self._draw_prompt(self.prompt)