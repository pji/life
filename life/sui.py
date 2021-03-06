"""
sui
~~

The user interface for Conway's Game of Life.
"""
from abc import ABC, abstractmethod
from os import listdir
from copy import deepcopy
from time import sleep
from typing import Any, List, Optional, Sequence, Tuple

from blessed import Terminal

from life.grid import Grid


# Complex type aliases for type hints. See the following for more info:
# https://docs.python.org/3/library/typing.html
_ArgList = Sequence[Any]
_Command = Tuple[str, Optional[_ArgList]]

# Useful terminal escape sequences:
DOWN = '\x1b[B'
UP = '\x1b[A'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'


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
    
    def input(self) -> _Command:
        """Get and handle input from the user."""
        cmd = None
        prompt = ''
        while not cmd:
            self._draw_prompt(prompt)
            with self.term.cbreak():
                raw_input = self.term.inkey()
            try:
                cmd = self.commands[raw_input]
            except KeyError:
                self._draw_prompt('')
                sleep(.05)
                prompt = 'Invalid command. Please try again.'
        return (cmd,)
    
    @abstractmethod
    def update_ui(self):
        """Update the terminal display."""


# State classes.
class Autorun(State):
    """Automatically advance the generation of the grid."""
    menu = 'Press any key to exit autorun.'
    
    def exit(self) -> 'Core':
        """Exit autorun state."""
        return Core(self.data, self.term)
    
    def input(self) -> _Command:
        """Get and handle input from the user."""
        cmd = 'run'
        with self.term.cbreak():
            raw_input = self.term.inkey(timeout=0.005)
        if raw_input:
            cmd = 'exit'
        return (cmd,)
    
    def run(self) -> 'Autorun':
        """Advance the generation of the grid."""
        self.data.next_generation()
        return self
    
    def update_ui(self):
        """Draw the UI for autorun state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)


class Core(State):
    """The standard state of the UI. This is used to manually progress 
    the grid and switch to other states.
    """
    commands = {
        'a': 'autorun',
        'c': 'clear',
        'e': 'edit',
        'l': 'load',
        'n': 'next',
        'r': 'random',
        's': 'save',
        'u': 'rule',
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
    
    def autorun(self) -> 'Autorun':
        """Command method. Switch to autorun state."""
        return Autorun(self.data, self.term)
    
    def clear(self) -> 'Core':
        """Command method. Clear the grid."""
        self.data.clear()
        return self
    
    def edit(self) -> 'Edit':
        """Command method. Switch to edit state."""
        return Edit(self.data, self.term)
    
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
    
    def rule(self) -> 'Rule':
        """Command method. Switch to rule state."""
        return Rule(self.data, self.term)
    
    def save(self) -> 'Load':
        """Command method. Switch to save state."""
        return Save(self.data, self.term)
    
    def update_ui(self):
        """Draw the UI for the core state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)
    

class Edit(State):
    """The state for manually editing the grid."""
    commands = {
        UP: 'up',
        DOWN: 'down',
        LEFT: 'left',
        RIGHT: 'right',
        'e': 'exit',
        ' ': 'flip',
        'r': 'restore',
        's': 'snapshot',
    }
    menu = ('(\u2190\u2191\u2192\u2193) Move, (space) Flip, (E)xit, '
            '(R)estore, (S)napshot')
    
    def __init__(self, data:Grid, term:Terminal):
        """Initialize an instance of Edit."""
        super().__init__(data, term)
        self.row = self.data.height // 2
        self.col = self.data.width // 2

    def _draw_cursor(self):
        """Display the cursor in the state UI."""
        y = self.row // 2
        
        # Figure out whether either of the cells sharing the location 
        # are alive.
        alive = []
        char = ''
        if self.row % 2:
            next_row = (self.row - 1) % self.data.height
            alive.append(self.data[next_row][self.col])
            alive.append(self.data[self.row][self.col])
            char = '\u2584'
        else:
            next_row = (self.row + 1) % self.data.height
            alive.append(self.data[self.row][self.col])
            alive.append(self.data[next_row][self.col])
            char = '\u2580'
        
        # Figure out which character and color is needed for the 
        # cursor. The cursor will be green if on a dead cell and 
        # bright green if on a live cell. However, whether the 
        # colors or foreground or background gets complicated 
        # when both cells in the location are alive.
        if alive == [False, False]:
            color = self.term.green
        elif alive == [True, True]:
            color = self.term.bright_green_on_bright_white
        elif alive == [True, False] and not self.row % 2:
            color = self.term.bright_green
        elif alive == [True, False]:
            color = self.term.green_on_bright_white
        elif alive == [False, True] and not self.row % 2:
            color = self.term.green_on_bright_white
        else:
            color = self.term.bright_green
        
        print(self.term.move(y, self.col) + color + char 
              + self.term.bright_white_on_black)
        
    def _move_cursor(self, d_row:int, d_col:int):
        """Move the cursor and update the UI.
        
        :param d_row: How much to change the row by.
        :param d_col: How much to change the column by.
        """
        self.row += d_row
        self.col += d_col
        self.row = self.row % self.data.height
        self.col = self.col % self.data.width
        self._draw_state()
        self._draw_cursor()
    
    def down(self) -> 'Edit':
        """Command method. Move the cursor down one row."""
        self._move_cursor(1, 0)
        return self
    
    def exit(self) -> 'Core':
        """Command method, switch to the Core state."""
        return Core(self.data, self.term)
    
    def flip(self) -> 'Edit':
        """Command method. Flip the state of the current cell."""
        self.data.flip(self.row, self.col)
        self._draw_state()
        self._draw_cursor()
        return self
    
    def left(self) -> 'Edit':
        """Command method. Move the cursor left one column."""
        self._move_cursor(0, -1)
        return self
    
    def right(self) -> 'Edit':
        """Command method. Move the cursor right one column."""
        self._move_cursor(0, 1)
        return self
    
    def restore(self) -> 'Edit':
        """Restore the snapshot grid state."""
        load = Load(self.data, self.term)
        load.load('pattern/.snapshot.txt')
        return self
    
    def snapshot(self) -> 'Edit':
        """Save the current grid state as a snapshot."""
        self._draw_prompt('Saving...')
        save = Save(self.data, self.term)
        save.save('.snapshot.txt')
        return self
    
    def up(self) -> 'Edit':
        """Command method. Move the cursor up one row."""
        self._move_cursor(-1, 0)
        return self
    
    def update_ui(self):
        """Draw the UI for the edit state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)
        self._draw_cursor()


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
        '\n': 'load',
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
        
        self.files = sorted(listdir(self.path))
        for index in range(len(self.files)):
            name = self.files[index]
            if index == self.selected:
                name = self.term.on_green + name + self.term.on_black
            print(self.term.move(index, 0) + name + self.term.clear_eol)
        
        if len(self.files) < height:
            for y in range(len(self.files), height):
                print(self.term.move(y, 0) + self.term.clear_eol)
    
    def _normalize_loaded_text(self, text:str, live: str = 'x') -> List[list]:
        """Convert a pattern saved as a text file into grid data.
        
        :param text: The pattern as text.
        :param live: The character that represents an alive cell.
        """
        new = []
        for line in text:
            row = []
            for char in line:
                if char.lower() == live:
                    row.append(True)
                else:
                    row.append(False)
            new.append(row)
        return new
    
    def down(self) -> 'Load':
        """Command method. Select the next file in the list."""
        self.selected += 1
        self.selected = self.selected % len(self.files)
        return self
    
    def exit(self) -> 'Core':
        """Command method. Exit load state."""
        return Core(self.data, self.term)
    
    def load(self, filename: str = None) -> 'Core':
        """Load the selected file and return to core state."""
        if not filename:
            filename = self.path + self.files[self.selected]
        with open(filename, 'r') as fh:
            raw = fh.readlines()
        normal = self._normalize_loaded_text(raw)
        self.data.replace(normal)
        return Core(self.data, self.term)
    
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


class Rule(State):
    """Change the rules of the grid."""
    def __init__(self, data:Grid, term:Terminal):
        super().__init__(data, term)
        self.menu = ('Enter the rules in BS notation. (Current rule: '
                     f'{self.data.rule})')
    
    def change(self, rule:str) -> 'Core':
        """Change the rules of the grid."""
        self.data.rule = rule
        return Core(self.data, self.term)
    
    def exit(self) -> 'Core':
        """Exit rule state."""
        return Core(self.data, self.term)
        
    def input(self) -> _Command:
        """Get a rule from the user."""
        y = self.data.height + 2
        rule = input(self.term.move(y, 0) + '> ')
        if rule:
            return ('change', rule)
        return ('exit',)
    
    def update_ui(self):
        """Draw the UI for autorun state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)


class Save(State):
    """The state for saving the grid state to a file."""
    menu = 'Enter name for save file.'
    path = 'pattern/'
    
    def _draw_state(self):
        """List the files available to be loaded."""
        height = self.data.height // 2
        if self.data.height % 2:
            height += 1
        
        self.files = listdir(self.path)
        for index in range(len(self.files)):
            name = self.files[index]
            print(self.term.move(index, 0) + name + self.term.clear_eol)
        
        if len(self.files) < height:
            for y in range(len(self.files), height):
                print(self.term.move(y, 0) + self.term.clear_eol)
    
    def _remove_padding(self, data: Sequence[list]) -> Grid:
        """Remove empty rows and columns surrounding the pattern."""
        # Find the first row with the pattern.
        y_start = 0
        while True not in data[y_start] and y_start < len(data):
            y_start += 1
        
        # Find last row with the pattern.
        y_end = len(data)
        while True not in data[y_end -1] and y_end > 0:
            y_end -= 1
        
        # Find first column with the pattern.
        x_start = 0
        while (not any(data[i][x_start] for i in range(len(data))) 
                and x_start < len(data[0])):
            x_start += 1
        
        # Find last column with pattern.
        x_end = len(data[0])
        while (not any(data[i][x_end - 1] for i in range(len(data))) 
                and x_start > 0):
            x_end -= 1
        
        return [row[x_start:x_end] for row in data[y_start:y_end]]
    
    def input(self) -> _Command:
        """Get a file name from the user."""
        y = self.data.height + 2
        filename = input(self.term.move(y, 0) + '> ')
        return ('save', filename)
    
    def save(self, filename:str) -> 'Core':
        """Save the current grid state to a file.
        
        :param filename: The name of the file to save.
        """
        grid_ = deepcopy(self.data)
        grid_._data = self._remove_padding(grid_._data)
        with open(self.path + filename, 'w') as fh:
            fh.write(str(grid_))
        return Core(self.data, self.term)
    
    def update_ui(self):
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
            load = Load(data, term)
            load.load('pattern/title.txt')
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