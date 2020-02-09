"""
sui
~~

The user interface for Conway's Game of Life.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence, Tuple

from blessed import Terminal

from life.grid import Grid


# Complex type aliases for type hints. See the following for more info:
# https://docs.python.org/3/library/typing.html
_ArgList = Sequence[Any]
_Command = Tuple[str, Optional[_ArgList]]


# Base class.
class State(ABC):
    """An abstract base class for UI states."""
    def __init__(self, data:Grid, term:Terminal):
        """Initialize a State object.
        
        :param data: The grid object for the current game of life.
        :param term: The terminal the game of life is being run in.
        """
        self.term = term
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
    def input(self) -> _Command:
        """Get and handle input from the user."""
    
    @abstractmethod
    def update_ui(self):
        """Update the terminal display."""


# State classes.
class Core(State):
    """The standard state of the UI. This is used to manually progress 
    the grid and switch to other states.
    """
    menu = {
        'q': 'quit',
    }
    
    def input(self) -> _Command:
        """Validate the user's command and return it."""
        with self.term.cbreak():
            cmd = self.term.inkey()
        return (self.menu[cmd],)
    
    def quit(self) -> 'End':
        """Command method. Quit the game of life."""
        return End()
    
    def update_ui(self):
        """Draw the UI for the core state."""
        raise NotImplementedError()
    

class End(State):
    """A state that terminates the game of life."""
    def __init__(self):
        """Initialize an instance of End."""
        pass
    
    def input(self):
        """This should never be called on an End object."""
        raise NotEmplementedError('End objects do not get input.')
    
    def update_ui(self):
        """Do not change the UI."""
        pass


class Start(State):
    """The starting state for the UI."""
    menu = 'Copyright © 2020 Paul J. Iutzi'
    prompt = 'Press any key to continue.'
    
    def __init__(self, data: Grid = None, term: Terminal = None):
        """Initialize a Start object.
        
        :param data: (Optional.) The grid object for the current 
            game of life.
        :param term: (Optional.) The terminal the game of life is 
            being run in.
        """
        if not term:
            term = Terminal()
        if not data:
            data = Grid(term.width, (term.height - 3) * 2)
        super().__init__(data, term)
    
    def input(self) -> _Command:
        """Return a Core object."""
        with self.term.cbreak():
            self.term.inkey()
        return ('run',)
    
    def run(self) -> Core:
        """Return a Core object to start the game of life."""
        return Core(self.data, self.term)
    
    def update_ui(self):
        """Draw the initial display state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)
        self._draw_prompt(self.prompt)


def main():
    state = Start()
    state.update_ui()
    while not isinstance(state, End):
        cmd, *args = state.input()
        state = getattr(state, cmd)(*args)