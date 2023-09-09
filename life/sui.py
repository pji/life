"""
sui
~~

The user interface for Conway's Game of Life.
"""
from abc import ABC, abstractmethod
from argparse import ArgumentParser
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
SDOWN = '\x1b[1;2B'
SUP = '\x1b[1;2A'
SLEFT = '\x1b[1;2D'
SRIGHT = '\x1b[1;2C'


# Base class.
class State(ABC):
    commands: dict = {}

    """An abstract base class for UI states."""
    def __init__(
        self,
        data: Grid,
        term: Terminal,
        origin_y: int | None = None,
        origin_x: int | None = None,
        pace: float = 0
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
        self.pace = pace

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
        shape = ((self.term.height - 3) * 2, self.term.width)
        return self.data.view(origin, shape)

    def asdict(self) -> dict:
        """Get the parameters of the state as a dictionary."""
        return {
            'data': self.data,
            'term': self.term,
            'origin_x': self.origin_x,
            'origin_y': self.origin_y,
            'pace': self.pace,
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
    commands = {
        LEFT: ('slower',),
        RIGHT: ('faster',),
        'x': ('exit',),
    }
    menu = '(\u2190) Slower, (\u2192) Faster, e(X)it'

    def exit(self) -> 'Core':
        """Exit autorun state."""
        return Core(**self.asdict())

    def faster(self) -> 'Autorun':
        """Command method. Decrease the time between ticks."""
        self.pace -= 0.01
        if self.pace < 0.0:
            self.pace = 0.0
        return self

    def input(self) -> Command:
        """Get and handle input from the user."""
        cmd = ('run',)
        with self.term.cbreak():
            raw_input = self.term.inkey(timeout=0.001)
        if raw_input:
            if raw_input in self.commands:
                cmd = self.commands[raw_input]
        return cmd

    def run(self) -> 'Autorun':
        """Advance the generation of the grid."""
        if self.pace:
            sleep(self.pace)
        self.data.tick()
        return self

    def slower(self) -> 'Autorun':
        """Command method. Increase the time between ticks."""
        self.pace += 0.01
        return self

    def update_ui(self):
        """Draw the UI for autorun state."""
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)


class Config(State):
    """The state for changing the configuration settings of the grid."""
    commands = {
        DOWN: 'down',
        UP: 'up',
        'x': 'exit',
        '\n': 'select',
    }
    menu = '(\u2191\u2192) Move, (\u23ce) Select, e(X)it'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.selected = 0
        self.settings = [
            'rule',
            'wrap',
        ]

    @property
    def rule(self) -> str:
        return self.data.rule

    @rule.setter
    def rule(self, value: str) -> None:
        self.data.rule = value

    @property
    def wrap(self) -> bool:
        return self.data.wrap

    @wrap.setter
    def wrap(self, value) -> None:
        self.data.wrap = value

    def _draw_state(self) -> None:
        """Draw the configuration to the screen."""
        height = self.data.height // 2
        if self.data.height % 2:
            height += 1

        for i, setting in enumerate(self.settings):
            value = getattr(self, setting)
            line = str(self.term.move(i, 0))
            if self.selected == i:
                line += self.term.black_on_green
            line += f'{setting.title()}: {value}' + self.term.clear_eol
            if self.selected == i:
                line += self.term.normal
            print(line)

        if len(self.settings) < height:
            for y in range(len(self.settings), height):
                print(self.term.move(y, 0) + self.term.clear_eol)

    def down(self) -> 'Config':
        """Command method. Select the next setting in the list."""
        self.selected += 1
        self.selected %= len(self.settings)
        return self

    def exit(self) -> 'Core':
        """Command method. Exit config mode and return to the core."""
        return Core(**self.asdict())

    def select(self) -> Union['Config', 'Rule']:
        """Command method. Change the selected setting."""
        state: Union['Config', 'Rule'] = self
        setting = self.settings[self.selected]

        if setting == 'rule':
            state = Rule(**self.asdict())

        else:
            current = getattr(self, setting)
            setattr(self, setting, not current)

        return state

    def up(self) -> 'Config':
        """Command method. Select the previous setting in the list."""
        self.selected -= 1
        self.selected %= len(self.settings)
        return self

    def update_ui(self) -> None:
        """Update the terminal display."""
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
        'f': 'config',
        'l': 'load',
        'n': 'next',
        'r': 'random',
        's': 'save',
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

    def config(self) -> 'Config':
        """Command method. Switch to config state."""
        return Config(**self.asdict())

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
        DOWN: 'down',
        LEFT: 'left',
        RIGHT: 'right',
        UP: 'up',
        SDOWN: 'down_10',
        SLEFT: 'left_10',
        SRIGHT: 'right_10',
        SUP: 'up_10',
        ' ': 'flip',
        'x': 'exit',
        'r': 'restore',
        's': 'snapshot',
    }
    menu = (
        '(\u2190\u2191\u2192\u2193) Move, (space) Flip, '
        '(R)estore, (S)napshot, e(X)it'
    )

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

    def down_10(self) -> 'Edit':
        """Command method. Move the cursor down one row."""
        self._move_cursor(10, 0)
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

    def left_10(self) -> 'Edit':
        """Command method. Move the cursor left ten columns."""
        self._move_cursor(0, -10)
        return self

    def right(self) -> 'Edit':
        """Command method. Move the cursor right one column."""
        self._move_cursor(0, 1)
        return self

    def right_10(self) -> 'Edit':
        """Command method. Move the cursor right ten columns."""
        self._move_cursor(0, 10)
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

    def up_10(self) -> 'Edit':
        """Command method. Move the cursor up ten rows."""
        self._move_cursor(-10, 0)
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
        'f': 'file',
        'x': 'exit',
        '\n': 'load',
    }
    menu = '(\u2191\u2192) Move, (\u23ce) Select, (F)rom file, e(X)it'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.files: list[str] = []
        self.path = files(life.pattern)
        self.selected = 0

    def _draw_state(self):
        """Display the files available to be loaded."""
        height = self.term.height - 3

        self._get_files()
        start = 0
        stop = height
        if self.selected > height - 1:
            stop = self.selected + 1
            start = stop - height
        for index, name in enumerate(self.files[start:stop]):
            path = self.path / name
            if path.is_dir():
                name = '\u25b8 ' + name
            if index + start == self.selected:
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
        return Core(**self.asdict())

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
        file: str | Path = Path(str(files(life.pattern))) / 'title.txt',
        rule: str = 'B3/S23',
        wrap: bool = True,
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
            load.load(file)
        super().__init__(data, term, *args, **kwargs)
        self.file = file
        self.wrap = wrap
        self.rule = rule

    @property
    def rule(self) -> str:
        return self.data.rule

    @rule.setter
    def rule(self, value: str) -> None:
        self.data.rule = value

    @property
    def wrap(self) -> bool:
        return self.data.wrap

    @wrap.setter
    def wrap(self, value: bool) -> None:
        self.data.wrap = value

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
    p = ArgumentParser(
        description='A Python implementation of Conway\'s Game of Life.',
        prog='life'
    )
    p.add_argument(
        '-f', '--file',
        help='A file to load into the Game of Life.',
        action='store',
        type=str
    )
    p.add_argument(
        '-p', '--pace',
        help='The delay between ticks when autorunning.',
        action='store',
        type=float
    )
    p.add_argument(
        '-r', '--rule',
        help='The rule for the Game of Life.',
        action='store',
        type=str
    )
    p.add_argument(
        '-W', '--no_wrap',
        help='The grid should not wrap at the edges.',
        action='store_true'
    )
    args = p.parse_args()

    term = Terminal()
    with term.fullscreen(), term.hidden_cursor():
        kwargs = {'term': term,}
        if args.file:
            kwargs['file'] = args.file.strip()
        if args.no_wrap:
            kwargs['wrap'] = False
        if args.pace:
            kwargs['pace'] = args.pace
        if args.rule:
            kwargs['rule'] = args.rule.strip()
        state = Start(**kwargs)
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
