"""
sui
~~

The user interface for Conway's Game of Life.
"""
from abc import ABC, abstractmethod
from os import listdir
from typing import Any, Optional, Sequence, Tuple

from blessed import Terminal

from life.grid import Grid


# Complex type aliases for type hints. See the following for more info:
# https://docs.python.org/3/library/typing.html
_ArgList = Sequence[Any]
_Command = Tuple[str, Optional[_ArgList]]

# Useful terminal escape sequences:
DOWN = '\x1b[B'
UP = '\x1b[A'


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
        y = -(self.data.height // -2) + 1
        print(self.term.move(y, 0) + cmds + self.term.clear_eol, end='', 
              flush=True)
    
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
        print(self.term.move(y, 0) + msg + self.term.clear_eol, 
              end='', flush=True)
    
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
    commands = {
        'c': 'clear',
        'l': 'load',
        'n': 'next',
        'r': 'random',
        'q': 'quit',
    }
    
    @property
    def menu(self):
        cmds = []
        for key in self.commands:
            index = self.commands[key].index(key)
            cmd = (f'{self.commands[key][0:index]}({key.upper()})'
                   f'{self.commands[key][index + 1:]}')
            cmds.append(cmd)
        return ', '.join(cmds)
    
    def clear(self) -> 'Core':
        """Command method. Clear the grid."""
        self.data.clear()
        return self
    
    def input(self) -> _Command:
        """Validate the user's command and return it."""
        self._draw_prompt('> ')
        with self.term.cbreak():
            cmd = self.term.inkey()
        return (self.commands[cmd],)
    
    def load(self) -> 'Load':
        """Command method. Switch to load state."""
        return Load(self.data, self.term)
    
    def next(self) -> 'Core':
        """Command method. Run the next generation of the grid."""
        self.data.next_generation()
        return self
    
    def quit(self) -> 'End':
        """Command method. Quit the game of life."""
        return End()
    
    def random(self) -> 'Core':
        """Command method. Randomize the values in the grid."""
        self.data.randomize()
        return self
    
    def update_ui(self):
        """Draw the UI for the core state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)
    

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


class Load(State):
    """The state for loading patterns from a file."""
    commands = {
        DOWN: 'down',
        UP: 'up',
        'e': 'exit',
    }
    menu = '(\u2191\u2192) Move, (\u23ce) Select, (E)xit'
    path = 'pattern/'
    files = []
    selected = 0
    
    def _draw_state(self):
        """List the files available to be loaded."""
        height = self.data.height // 2
        if self.data.height % 2:
            height += 1
        
        self.files = listdir(self.path)
        for index in range(len(self.files)):
            name = self.files[index]
            if index == self.selected:
                name = self.term.on_green + name + self.term.on_black
            print(self.term.move(index, 0) + name + self.term.clear_eol)
        
        if len(self.files) < height:
            for y in range(len(self.files), height):
                print(self.term.move(y, 0) + self.term.clear_eol)
    
    def down(self) -> 'Load':
        """Command method. Select the next file in the list."""
        self.selected += 1
        self.selected = self.selected % len(self.files)
        return self
    
    def exit(self) -> 'Core':
        """Command method. Exit load state."""
        return Core(self.data, self.term)
    
    def input(self) -> _Command:
        """Get command input from the user."""
        self._draw_prompt('')
        with self.term.cbreak():
            cmd = self.term.inkey()
        return (self.commands[cmd],)
    
    def up(self) -> 'Load':
        """Command method. Select the previous file in the list."""
        self.selected -= 1
        self.selected = self.selected % len(self.files)
        return self
    
    def update_ui(self):
        """Draw the load state UI."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)


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
        self._draw_prompt(self.prompt)
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


def main():
    term = Terminal()
    with term.fullscreen(), term.hidden_cursor():
        state = Start(term=term)
        while not isinstance(state, End):
            state.update_ui()
            cmd, *args = state.input()
            state = getattr(state, cmd)(*args)


if __name__ == '__main__':
    import traceback as tb
    
    try:
        main()
    except Exception as ex:
        with open('exception.log', 'w') as fh:
            fh.write(str(type(ex)) + '\n')
            fh.write(str(ex.args) + '\n')
            tb_str = ''.join(tb.format_tb(ex.__traceback__))
            fh.write(tb_str)
        raise ex