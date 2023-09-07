"""
sui
~~

The user interface for Conway's Game of Life.
"""
from abc import ABC, abstractmethod
from copy import deepcopy
from importlib.abc import Traversable
from importlib.resources import files
from pathlib import Path
from time import sleep
from typing import Any, List, Sequence, Union

import numpy as np
from blessed import Terminal
from numpy.typing import NDArray

import life.pattern
from life import util
from life.life import Grid


# Types.
Command = tuple[str] | tuple[str, str]

# Useful terminal escape sequences:
DOWN = '\x1b[B'
UP = '\x1b[A'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'


# Base class.
class State(ABC):
    commands: dict = {}

    """An abstract base class for UI states."""
    def __init__(
        self,
        data: Grid,
        term: Terminal,
        origin_y: int | None = None,
        origin_x: int | None = None
    ) -> None:
        """Initialize a State object.

        :param data: The grid object for the current game of life.
        :param term: The terminal the game of life is being run in.
        """
        self.data = data
        self.term = term
        if origin_x is None:
            origin_x = (data.width - term.width) // 2
        self.origin_x = origin_x
        if origin_y is None:
            origin_y = (data.height - (term.height - 3) * 2) // 2
        self.origin_y = origin_y

    def _char_for_state(self, top, bottom) -> str:
        """Return the character to draw based on the state of the cell."""
        if top and bottom:
            return '\u2588'
        elif top and not bottom:
            return '\u2580'
        elif not top and bottom:
            return '\u2584'
        return ' '

    def _draw_commands(self, cmds: str = '') -> None:
        """Draw the available commands."""
        y = -(self.data.height // -2) + 1
        print(
            self.term.move(y, 0) + cmds + self.term.clear_eol,
            end='',
            flush=True
        )

    def _draw_state(self) -> None:
        """Draw the grid to the terminal."""
        data: np.ndarray = self._get_window()
        if len(data) % 2:
            data = np.pad(data, ((0, 1), (0, 0)))
        for i in range(0, len(data), 2):
            cells = []
            for j in range(0, len(data[i])):
                char = self._char_for_state(data[i][j], data[i + 1][j])
                cells.append(char)
            print(self.term.move(i // 2, 0) + ''.join(cells))

    def _draw_prompt(self, msg: str = '> ') -> None:
        """Draw the command prompt."""
        y = -(self.data.height // -2) + 2
        print(
            self.term.move(y, 0) + msg + self.term.clear_eol,
            end='',
            flush=True
        )

    def _draw_rule(self) -> None:
        """Draw the a horizontal rule."""
        width = self.data.width
        y = -(self.data.height // -2)
        print(self.term.move(y, 0) + '\u2500' * width)

    def _get_window(self) -> NDArray[np.bool_]:
        """Get the visible area of the grid."""
        origin = (self.origin_y, self.origin_x)
        shape = (self.term.height, self.term.width)
        return self.data.view(origin, shape)

    def asdict(self) -> dict:
        """Get the parameters of the state as a dictionary."""
        return {
            'data': self.data,
            'term': self.term,
            'origin_x': self.origin_x,
            'origin_y': self.origin_y,
        }

    def input(self) -> Command:
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
    def update_ui(self) -> None:
        """Update the terminal display."""


# State classes.
class Autorun(State):
    """Automatically advance the generation of the grid."""
    menu = 'Press any key to exit autorun.'

    def exit(self) -> 'Core':
        """Exit autorun state."""
        return Core(**self.asdict())

    def input(self) -> Command:
        """Get and handle input from the user."""
        cmd = 'run'
        with self.term.cbreak():
            raw_input = self.term.inkey(timeout=0.005)
        if raw_input:
            cmd = 'exit'
        return (cmd,)

    def run(self) -> 'Autorun':
        """Advance the generation of the grid."""
        self.data.tick()
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
        return Autorun(**self.asdict())

    def clear(self) -> 'Core':
        """Command method. Clear the grid."""
        self.data.clear()
        return self

    def edit(self) -> 'Edit':
        """Command method. Switch to edit state."""
        return Edit(**self.asdict())

    def load(self) -> 'Load':
        """Command method. Switch to load state."""
        return Load(**self.asdict())

    def next(self) -> 'Core':
        """Command method. Run the next generation of the grid."""
        self.data.tick()
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
        return Rule(**self.asdict())

    def save(self) -> 'Save':
        """Command method. Switch to save state."""
        return Save(**self.asdict())

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

    def __init__(self, *args, **kwargs):
        """Initialize an instance of Edit."""
        super().__init__(*args, **kwargs)
        self.row = self.data.height // 2
        self.col = self.data.width // 2
        self.path = Path('.snapshot.txt')

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
        return Core(**self.asdict())

    def flip(self) -> 'Edit':
        """Command method. Flip the state of the current cell."""
        self.data.flip(self.col, self.row)
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
        load.load(self.path)
        return self

    def snapshot(self) -> 'Edit':
        """Save the current grid state as a snapshot."""
        self._draw_prompt('Saving...')
        save = Save(self.data, self.term)
        save.save(self.path)
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
        'f': 'file',
        '\n': 'load',
    }
    menu = '(\u2191\u2192) Move, (\u23ce) Select, (E)xit, (F)rom file'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.files: list[str] = []
        self.path = files(life.pattern)
        self.selected = 0

    def _draw_state(self):
        """Display the files available to be loaded."""
        height = self.data.height // 2
        if self.data.height % 2:
            height += 1

        self._get_files()
        for index, name in enumerate(self.files):
            path = self.path / name
            if path.is_dir():
                name = '\u25b8 ' + name
            if index == self.selected:
                name = self.term.on_green + name + self.term.normal
            print(self.term.move(index, 0) + name + self.term.clear_eol)

        if len(self.files) < height:
            for y in range(len(self.files), height):
                print(self.term.move(y, 0) + self.term.clear_eol)

    def _get_files(self):
        """List the files available to be loaded."""
        files = sorted(
            path.name for path in self.path.iterdir()
            if path.is_file() and not path.name.startswith('__')
        )
        dirs = sorted(
            path.name for path in self.path.iterdir()
            if path.is_dir() and not path.name.startswith('__')
        )
        self.files = dirs
        for name in files:
            self.files.append(name)
        self.files.insert(0, '..')

    def down(self) -> 'Load':
        """Command method. Select the next file in the list."""
        self.selected += 1
        self.selected = self.selected % len(self.files)
        return self

    def exit(self) -> 'Core':
        """Command method. Exit load state."""
        return Core(**self.asdict())

    def file(self, path: Path = Path.cwd()) -> 'Load':
        """Command method. Select from files in the current working
        directory.
        """
        self.path = path
        return self

    def load(
        self, filename: str | Path | Traversable | None = None
    ) -> Union['Core', 'Load']:
        """Load the selected file and return to core state."""
        if filename is None:
            filename = self.path / self.files[self.selected]
        if isinstance(filename, Traversable):
            filename = str(filename)
        filename = Path(filename)

        if filename.is_dir():
            self.path = filename
            self.selected = 0
            return self

        elif filename.exists():
            with open(filename, 'r') as fh:
                raw = fh.readlines()
            if filename.suffix == '.cells':
                normal = cells(raw)
            else:
                normal = pattern(raw)
            self.data.replace(normal)
        return Core(**self.asdict())

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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.menu = ('Enter the rules in BS notation. (Current rule: '
                     f'{self.data.rule})')

    def change(self, rule:str) -> 'Core':
        """Change the rules of the grid."""
        self.data.rule = rule
        return Core(self.data, self.term)

    def exit(self) -> 'Core':
        """Exit rule state."""
        return Core(**self.asdict())

    def input(self) -> Command:
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
    path = Path('')

    def _draw_state(self):
        """List the files available to be loaded."""
        height = self.data.height // 2
        if self.data.height % 2:
            height += 1

        self.files = sorted(path for path in self.path.iterdir())
        for index, path in enumerate(self.files):
            path = Path(path)
            name = path.name
            print(self.term.move(index, 0) + name + self.term.clear_eol)

        if len(self.files) < height:
            for y in range(len(self.files), height):
                print(self.term.move(y, 0) + self.term.clear_eol)

    def _remove_padding(self, data: np.ndarray) -> list[Any]:
        """Remove empty rows and columns surrounding the pattern."""
        # Find the first row with the pattern.
        y_start = 0
        while True not in data[y_start] and y_start < len(data):
            y_start += 1

        # Find last row with the pattern.
        y_end = len(data)
        while True not in data[y_end - 1] and y_end > 0:
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

    def input(self) -> Command:
        """Get a file name from the user."""
        y = self.data.height + 2
        filename = input(self.term.move(y, 0) + '> ')
        return ('save', filename)

    def save(self, filename: str | Path) -> 'Core':
        """Save the current grid state to a file.

        :param filename: The name of the file to save.
        """
        grid_ = deepcopy(self.data)
        grid_._data = np.array(self._remove_padding(grid_._data), dtype=bool)
        path = Path(filename)
        if '/' not in str(filename):
            path = self.path / filename
        with open(path, 'w') as fh:
            fh.write(str(grid_))
        return Core(**self.asdict())

    def update_ui(self):
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)


class Start(State):
    """The starting state for the UI."""
    menu = 'Copyright © 2020 Paul J. Iutzi'
    prompt = 'Press any key to continue.'

    def __init__(
        self,
        data: Grid | None = None,
        term: Terminal | None = None,
        *args, **kwargs
    ):
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
            pattern = files(life.pattern)
            path = Path(str(pattern))
            load.load(path / 'title.txt')
        super().__init__(data, term, *args, **kwargs)

    def input(self) -> Command:
        """Return a Core object."""
        self._draw_prompt(self.prompt)
        with self.term.cbreak():
            self.term.inkey()
        return ('run',)

    def run(self) -> Core:
        """Return a Core object to start the game of life."""
        return Core(**self.asdict())

    def update_ui(self):
        """Draw the initial display state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)


# File formats.
def cells(lines: list[str]) -> NDArray[np.bool_]:
    """Covert the contents of a .cells file into something :mod:`life`
    can understand.
    """
    filtered = [line.rstrip() for line in lines if not line.startswith('!')]
    width = max(len(line) for line in filtered)
    normal = [util.normalize_width(line, width) for line in filtered]
    return np.array(
        [util.char_to_bool(line, 'O') for line in normal],
        dtype=bool
    )


def pattern(lines: list[str]) -> NDArray[np.bool_]:
    """Convert the contents of a .pattern file into something :mod:`life`
    can understand.
    """
    lines = [line.rstrip() for line in lines]
    width = max(len(line) for line in lines)
    normal = [util.normalize_width(line, width) for line in lines]
    return np.array(
        [util.char_to_bool(line, 'X') for line in normal],
        dtype=bool
    )


# Mainline.
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
