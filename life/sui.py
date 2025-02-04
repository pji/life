"""
sui
~~

The user interface for Conway's Game of Life.
"""
from abc import ABC, abstractmethod
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from time import sleep
from typing import Sequence, Union

import numpy as np
from blessed import Terminal
from numpy.typing import NDArray

import life.pattern
from life import util
from life.codec import codecs, decode, encode
from life.life import Grid, InvalidRule


# Types.
Command = tuple[str] | tuple[str, str]

# Useful terminal escape sequences:
ESC = '\x1b'
DOWN = '\x1b[B'
UP = '\x1b[A'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'
SDOWN = '\x1b[1;2B'
SUP = '\x1b[1;2A'
SLEFT = '\x1b[1;2D'
SRIGHT = '\x1b[1;2C'


# Exceptions.
class CannotTakeInput(NotImplementedError):
    """The state is not allowed to take input."""


class InvalidSaveFormat(ValueError):
    """The given save file format was invalid."""


# Base class.
class State(ABC):
    """An abstract base class for UI states.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.State` object.
    :rtype: life.sui.State
    """
    commands: dict = {}
    _menu: str = ''

    def __init__(
        self,
        data: Grid,
        term: Terminal,
        origin_y: int | None = None,
        origin_x: int | None = None,
        pace: float = 0,
        show_generation: bool = False,
        user: str = '',
        comment: str = '',
        save_format: str = 'cells'
    ) -> None:
        """Initialize a State object."""
        self.data = data
        self.term = term

        self.comment = comment
        if origin_x is None:
            origin_x = (data.width - term.width) // 2
        self.origin_x = origin_x
        if origin_y is None:
            origin_y = (data.height - (term.height - 3) * 2) // 2
        self.origin_y = origin_y
        self.pace = pace
        self.save_format = save_format
        self.show_generation = show_generation
        self.user = user

    @property
    def menu(self) -> str:
        return self._menu

    @property
    def rule(self) -> str:
        return self.data.rule

    @rule.setter
    def rule(self, value: str) -> None:
        self.data.rule = value

    @property
    def save_format(self) -> str:
        return self._save_format

    @save_format.setter
    def save_format(self, value: str) -> None:
        if value not in codecs:
            raise InvalidSaveFormat('Invalid save format.')
        self._save_format = value

    @property
    def wrap(self) -> bool:
        return self.data.wrap

    @wrap.setter
    def wrap(self, value) -> None:
        self.data.wrap = value

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
        # y = -(self.data.height // -2) + 1
        y = self.term.height - 2
        print(
            self.term.move(y, 0) + cmds + self.term.clear_eol,
            end='',
            flush=True
        )

    def _draw_generation(self) -> None:
        """Draw the current generation to the terminal."""
        if self.show_generation:
            y = self.term.height - 3
            print(
                self.term.move(y, 0) + f'Generation: {self.data.generation}',
                end='',
                flush=True
            )

    def _draw_prompt(self, msg: str = '> ') -> None:
        """Draw the command prompt."""
        y = self.term.height - 1
        print(
            self.term.move(y, 0) + msg + self.term.clear_eol,
            end='',
            flush=True
        )

    def _draw_rule(self) -> None:
        """Draw the a horizontal rule."""
        width = self.term.width
        y = self.term.height - 3
        print(self.term.move(y, 0) + '\u2500' * width)

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

    def _expand_dir(self, path: str | Path) -> str:
        """Given the start of the name of a directory, if there is only
        one file or directory that starts with that name, return the
        rest of the characters of the name of that file or directory.
        """
        path = Path(path)
        matches = [
            child for child in path.parent.iterdir()
            if child.name.startswith(path.name)
        ]
        if len(matches) == 1:
            result = matches[0].name[len(path.name):]
            if matches[0].is_dir():
                result += '/'
            return result
        return ''

    def _get_text(self, y: int, x: int, is_path: bool = False) -> str:
        buffer = ''
        key = ''
        with self.term.cbreak():
            while key not in [ESC, '\n']:
                x_text = len(buffer)
                if key in ['\b', '\x7f']:
                    buffer = buffer[:-1]
                    x_text -= 1
                    key = ' '
                elif is_path and key == '\t':
                    key = self._expand_dir(buffer)
                    buffer += key
                else:
                    buffer += key
                print(
                    self.term.move(y, x + x_text) + key,
                    end='',
                    flush=True
                )
                key = self.term.inkey()
        if key == ESC:
            return ESC
        return buffer

    def _get_window(self) -> NDArray[np.bool_]:
        """Get the visible area of the grid."""
        origin = (self.origin_y, self.origin_x)
        shape = ((self.term.height - 3) * 2, self.term.width)
        return self.data.view(origin, shape)

    def asdict(self) -> dict:
        """Get the parameters of the state as a dictionary.

        :returns: A :class:`dict` object.
        :rtype: dict
        """
        return {
            'data': self.data,
            'term': self.term,
            'comment': self.comment,
            'origin_x': self.origin_x,
            'origin_y': self.origin_y,
            'pace': self.pace,
            'show_generation': self.show_generation,
            'user': self.user,
        }

    def input(self) -> Command:
        """Get and handle input from the user.

        :returns: A :class:`Command` object
        :rtype: Command
        """
        cmd: Command | str | None = None
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
        if isinstance(cmd, str):
            cmd = (cmd,)
        return cmd

    def update_ui(self) -> None:
        """Draw the UI for the edit state.

        :returns: `None`.
        :rtype: NoneType
        """
        self._draw_state()
        self._draw_rule()
        self._draw_commands(self.menu)


# State classes.
class Autorun(State):
    """A state that automatically advance the generation of the grid.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Autorun` object.
    :rtype: life.sui.Autorun

    Usage::

        >>> from blessed import Terminal
        >>> from life.life import Grid
        >>>
        >>> grid = Grid(5, 5)
        >>> term = Terminal()
        >>> state = Autorun(grid, term)
    """
    commands = {
        LEFT: ('slower',),
        RIGHT: ('faster',),
        'x': ('exit',),
        ' ': ('exit',)
    }
    _menu = '(\u2190) Slower, (\u2192) Faster, e(X)it'

    def exit(self) -> 'Core':
        """Exit autorun state.

        :returns: A :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from blessed import Terminal
            >>> from life.life import Grid
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Autorun(grid, term)
            >>>
            >>> state = state.exit()
            >>> type(state)
            <class 'life.sui.Core'>
        """
        return Core(**self.asdict())

    def faster(self) -> 'Autorun':
        """Command method. Decrease the time between ticks.

        :returns: A :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from blessed import Terminal
            >>> from life.life import Grid
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Autorun(grid, term, pace=0.2)
            >>>
            >>> state.pace
            0.2
            >>> state = state.faster()
            >>> state.pace
            0.19
        """
        self.pace -= 0.01
        if self.pace < 0.0:
            self.pace = 0.0
        return self

    def input(self) -> Command:
        """Get and handle input from the user.

        :returns: A :class:`tuple` object.
        :rtype: tuple
        """
        cmd = ('run',)
        with self.term.cbreak():
            raw_input = self.term.inkey(timeout=0.001)
        if raw_input:
            if raw_input in self.commands:
                cmd = self.commands[raw_input]
        return cmd

    def run(self) -> 'Autorun':
        """Advance the generation of the grid.

        :returns: A :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from blessed import Terminal
            >>> from life.life import Grid
            >>> import numpy as np
            >>>
            >>> a = np.array([
            ...     [False, False, False, False, False],
            ...     [False, True, True, True, False],
            ...     [False, False, False, True, False],
            ...     [False, False, True, False, False],
            ...     [False, False, False, False, False],
            ... ])
            >>> grid = Grid.from_array(a)
            >>> term = Terminal()
            >>> state = Autorun(grid, term)
            >>>
            >>> print(str(grid))
            .....
            .XXX.
            ...X.
            ..X..
            .....
            >>> state = state.run()
            >>> print(str(grid))
            ..X..
            ..XX.
            .X.X.
            .....
            .....
        """
        if self.pace:
            sleep(self.pace)
        self.data.tick()
        return self

    def slower(self) -> 'Autorun':
        """Command method. Increase the time between ticks.

        :returns: A :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from blessed import Terminal
            >>> from life.life import Grid
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Autorun(grid, term, pace=0.2)
            >>>
            >>> state.pace
            0.2
            >>> state = state.faster()
            >>> state.pace
            0.21
        """
        self.pace += 0.01
        return self

    def update_ui(self) -> None:
        """Draw the UI for autorun state.

        :returns: `None`.
        :rtype: NoneType
        """
        super().update_ui()
        self._draw_generation()


class Config(State):
    """The state for changing the configuration settings of the grid.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Config` object.
    :rtype: life.sui.Config

    Usage::

        >>> from blessed import Terminal
        >>> from life.life import Grid
        >>>
        >>> grid = Grid(5, 5)
        >>> term = Terminal()
        >>> state = Config(grid, term)
        >>> type(state)
        <class 'life.sui.Config'>
    """
    commands = {
        DOWN: 'down',
        UP: 'up',
        'x': 'exit',
        '\n': 'select',
    }
    _menu = '(\u2191\u2192) Move, (\u23ce) Select, e(X)it'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.selected = 0
        self.settings = [
            'comment',
            'pace',
            'rule',
            'save_format',
            'show_generation',
            'user',
            'wrap',
        ]

    def _draw_state(self) -> None:
        """Draw the configuration to the screen."""
        height = self.term.height

        for i, setting in enumerate(self.settings):
            label = setting.replace('_', ' ')
            value = getattr(self, setting)
            line = str(self.term.move(i, 0))
            if self.selected == i:
                line += self.term.black_on_green
            line += f'{label.title()}: {value}' + self.term.clear_eol
            if self.selected == i:
                line += self.term.normal
            print(line, end='', flush=True)

        if len(self.settings) < height:
            for y in range(len(self.settings), height):
                print(
                    self.term.move(y, 0) + self.term.clear_eol,
                    end='',
                    flush=True
                )

    def down(self) -> 'Config':
        """Command method. Select the next setting in the list.

        :returns: A :class:`life.sui.Config` object.
        :rtype: life.sui.Config

        Usage::

            >>> from blessed import Terminal
            >>> from life.life import Grid
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Config(grid, term)
            >>>
            >>> state.selected
            0
            >>> state = state.down()
            >>> state.selected
            1
        """
        self.selected += 1
        self.selected %= len(self.settings)
        return self

    def exit(self) -> 'Core':
        """Command method. Exit config mode and return to the core.

        :returns: A :class:`life.sui.Config` object.
        :rtype: life.sui.Config

        Usage::

            >>> from blessed import Terminal
            >>> from life.life import Grid
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Config(grid, term)
            >>>
            >>> state = state.exit()
            >>> type(state)
            <class 'life.sui.Core'>
        """
        return Core(**self.asdict())

    def select(self) -> 'Config':
        """Command method. Change the selected setting.

        :returns: A :class:`life.sui.Config` object.
        :rtype: life.sui.Config
        """
        def get_text_input(msg: str) -> str:
            y = self.term.height - 1
            self._draw_commands(msg)
            self._draw_prompt()
            return self._get_text(y, 2)

        setting = self.settings[self.selected]

        if setting == 'comment':
            msg = 'Enter a comment to add to the save file.'
            self.comment = get_text_input(msg)

        elif setting == 'pace':
            msg = 'Enter a number of seconds between each generation:'
            while True:
                try:
                    value = get_text_input(msg)
                    if value:
                        self.pace = float(value)
                except ValueError:
                    msg = 'Invalid float. ' + msg
                    continue
                break

        elif setting == 'rule':
            msg = (
                'Enter the rules in BS notation. (Current rule: '
                f'{self.data.rule})'
            )
            while True:
                try:
                    rule = get_text_input(msg)
                    if rule:
                        self.rule = rule
                except InvalidRule:
                    msg = 'Invalid rule. ' + msg
                    continue
                break

        elif setting == 'save_format':
            msg = 'Save file format. Options: cells, pattern, rle.'
            while True:
                try:
                    save_format = get_text_input(msg)
                    if save_format:
                        self.save_format = save_format
                except InvalidSaveFormat:
                    msg = 'Invalid save file format. ' + msg
                    continue
                break

        elif setting == 'user':
            msg = 'Enter a name to credit in the save file.'
            self.user = get_text_input(msg)

        else:
            current = getattr(self, setting)
            setattr(self, setting, not current)

        return self

    def up(self) -> 'Config':
        """Command method. Select the previous setting in the list.

        :returns: A :class:`life.sui.Config` object.
        :rtype: life.sui.Config

        Usage::

            >>> from blessed import Terminal
            >>> from life.life import Grid
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Config(grid, term)
            >>>
            >>> state.selected
            0
            >>> state = state.up()
            >>> state.selected
            6
        """
        self.selected -= 1
        self.selected %= len(self.settings)
        return self


class Core(State):
    """The standard state of the UI. This is used to manually progress
    the grid and switch to other states.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Core` object.
    :rtype: life.sui.Core

    Usage::

        >>> from life.life import Grid
        >>> from blessed import Terminal
        >>>
        >>> grid = Grid(5, 5)
        >>> term = Terminal()
        >>> state = Core(grid, term)
        >>> type(state)
        <class 'life.sui.Core'>
    """
    commands = {
        'a': 'autorun',
        'e': 'edit',
        'f': 'config',
        'l': 'load',
        'm': 'move',
        'n': 'next',
        'r': 'random',
        's': 'save',
        'q': 'quit',
    }

    @property
    def menu(self) -> str:
        """The text for the menu."""
        cmds = []
        for key in self.commands:
            index = self.commands[key].index(key)
            cmd = (f'{self.commands[key][0:index]}({key.upper()})'
                   f'{self.commands[key][index + 1:]}')
            cmds.append(cmd)
        return ', '.join(cmds)

    def autorun(self) -> 'Autorun':
        """Command method. Switch to autorun state.

        :returns: An :class:`life.sui.Autorun` object.
        :rtype: life.sui.Autorun

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>> state = state.autorun()
            >>> type(state)
            <class 'life.sui.Autorun'>
        """
        return Autorun(**self.asdict())

    def config(self) -> 'Config':
        """Command method. Switch to config state.

        :returns: An :class:`life.sui.Config` object.
        :rtype: life.sui.Config

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>> state = state.config()
            >>> type(state)
            <class 'life.sui.Config'>
        """
        return Config(**self.asdict())

    def edit(self) -> 'Edit':
        """Command method. Switch to edit state.

        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>> state = state.edit()
            >>> type(state)
            <class 'life.sui.Edit'>
        """
        return Edit(**self.asdict())

    def load(self) -> 'Load':
        """Command method. Switch to load state.

        :returns: An :class:`life.sui.Load` object.
        :rtype: life.sui.Load

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>> state = state.load()
            >>> type(state)
            <class 'life.sui.Load'>
        """
        return Load(**self.asdict())

    def move(self) -> 'Move':
        """Command method. Switch to the move state.

        :returns: An :class:`life.sui.Move` object.
        :rtype: life.sui.Move

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>> state = state.move()
            >>> type(state)
            <class 'life.sui.Move'>
        """
        return Move(**self.asdict())

    def next(self) -> 'Core':
        """Command method. Run the next generation of the grid.

        :returns: An :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> a = np.array([
            ...     [False, False, False, False, False],
            ...     [False, True, True, True, False],
            ...     [False, False, False, True, False],
            ...     [False, False, True, False, False],
            ...     [False, False, False, False, False],
            ... ])
            >>> grid = Grid.from_array(a)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>>
            >>> print(grid)
            .....
            .XXX.
            ...X.
            ..X..
            .....
            >>> state = state.next()
            >>> print(grid)
            ..X..
            ..XX.
            .X.X.
            .....
            .....
        """
        self.data.tick()
        return self

    def quit(self) -> 'End':
        """Command method. Quit the game of life.

        :returns: An :class:`life.sui.End` object.
        :rtype: life.sui.End

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>> state = state.end()
            >>> type(state)
            <class 'life.sui.End'>
        """
        return End(**self.asdict())

    def random(self) -> 'Core':
        """Command method. Randomize the values in the grid.

        :returns: An :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>> import numpy as np
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>>
            >>> # This line is just to seed the random number generator
            >>> # to ensure repeatability for testing the documentation.
            >>> # Do not do this is you want randomization.
            >>> grid.rng = np.random.default_rng(1138)
            >>>
            >>> state = Core(grid, term)
            >>>
            >>> print(grid)
            .....
            .....
            .....
            .....
            .....
            >>> state = state.random()
            >>> print(grid)
            ..XX.
            .XX.X
            X.X.X
            ..XX.
            XX...
        """
        self.data.randomize()
        return self

    def save(self) -> 'Save':
        """Command method. Switch to save state.

        :returns: An :class:`life.sui.Save` object.
        :rtype: life.sui.Save

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Core(grid, term)
            >>> state = state.save()
            >>> type(state)
            <class 'life.sui.Save'>
        """
        return Save(**self.asdict())

    def update_ui(self) -> None:
        """Draw the UI for the core state.

        :returns: `None`.
        :rtype: NoneType
        """
        super().update_ui()
        self._draw_generation()


class Edit(State):
    """The state for manually editing the grid.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Edit` object.
    :rtype: life.sui.Edit

    Usage::

        >>> from life.life import Grid
        >>> from blessed import Terminal
        >>>
        >>> grid = Grid(5, 5)
        >>> term = Terminal()
        >>> state = Edit(grid, term)
        >>> type(state)
        <class 'life.sui.Edit'>
    """
    commands = {
        DOWN: ('down', 1),
        LEFT: ('left', 1),
        RIGHT: ('right', 1),
        UP: ('up', 1),
        SDOWN: ('down', 10),
        SLEFT: ('left', 10),
        SRIGHT: ('right', 10),
        SUP: ('up', 10),
        ' ': 'flip',
        'c': 'clear',
        'r': 'restore',
        's': 'snapshot',
        'x': 'exit',
    }
    _menu = (
        '(\u2190\u2191\u2192\u2193) Move, (space) Flip, '
        '(C)lear, (R)estore, (S)napshot, e(X)it'
    )

    def __init__(self, *args, **kwargs):
        """Initialize an instance of Edit."""
        super().__init__(*args, **kwargs)
        self.row = self.data.height // 2
        self.col = self.data.width // 2
        self.path = Path('.snapshot.cells')

    # Private methods.
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

    def _move_cursor(self, d_row: int, d_col: int):
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

    # Public methods.
    def clear(self) -> 'Edit':
        """Command method. Clear the grid.

        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>> import numpy as np
            >>>
            >>> a = np.array([
            ...     [False, False, False, False, False],
            ...     [False, True, True, True, False],
            ...     [False, False, False, True, False],
            ...     [False, False, True, False, False],
            ...     [False, False, False, False, False],
            ... ])
            >>> grid = Grid.from_array(a)
            >>> term = Terminal()
            >>> state = Edit(grid, term)
            >>>
            >>> print(grid)
            .....
            .XXX.
            ...X.
            ..X..
            .....
            >>> state = state.clear()
            >>> print(grid)
            .....
            .....
            .....
            .....
            .....
        """
        self.data.clear()
        return self

    def down(self, distance: int = 1) -> 'Edit':
        """Command method. Move the cursor down.

        :param distance: (Optional.) How far to move. Defaults
            to `1`.
        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Edit(grid, term)
            >>>
            >>> state.col, state.row
            (2, 2)
            >>> state = state.down()
            >>> state.col, state.row
            (2, 3)
        """
        self._move_cursor(distance, 0)
        return self

    def exit(self) -> 'Core':
        """Command method, switch to the Core state.

        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Edit(grid, term)
            >>>
            >>> state = state.exit()
            >>> type(state)
            <class 'life.sui.Core'>
        """
        return Core(**self.asdict())

    def flip(self) -> 'Edit':
        """Command method. Flip the state of the current cell.

        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Edit(grid, term)
            >>>
            >>> state.row, state.col
            (2, 2)
            >>> print(grid)
            .....
            .....
            .....
            .....
            .....
            >>> grid.col, grid.row
            >>> state.flip()
            >>> print(grid)
            .....
            .....
            ..X..
            .....
            .....
        """
        self.data.flip(self.col, self.row)
        self.data.generation = 0
        self._draw_state()
        self._draw_cursor()
        return self

    def left(self, distance: int = 1) -> 'Edit':
        """Command method. Move the cursor left.

        :param distance: (Optional.) How far to move. Defaults
            to `1`.
        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Edit(grid, term)
            >>>
            >>> state.col, state.row
            (2, 2)
            >>> state = state.left()
            >>> state.col, state.row
            (2, 1)
        """
        self._move_cursor(0, distance * -1)
        return self

    def right(self, distance: int = 1) -> 'Edit':
        """Command method. Move the cursor right.

        :param distance: (Optional.) How far to move. Defaults
            to `1`.
        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Edit(grid, term)
            >>>
            >>> state.col, state.row
            (2, 2)
            >>> state = state.right()
            >>> state.col, state.row
            (2, 3)
        """
        self._move_cursor(0, distance)
        return self

    def restore(self) -> 'Edit':
        """Restore the snapshot grid state.

        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit
        """
        load = Load(self.data, self.term)
        load.load(self.path)
        return self

    def snapshot(self) -> 'Edit':
        """Save the current grid state as a snapshot.

        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit
        """
        self._draw_prompt('Saving...')
        save = Save(self.data, self.term)
        save.save(self.path)
        return self

    def up(self, distance: int = 1) -> 'Edit':
        """Command method. Move the cursor up.

        :param distance: (Optional.) How far to move. Defaults
            to `1`.
        :returns: An :class:`life.sui.Edit` object.
        :rtype: life.sui.Edit

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Edit(grid, term)
            >>>
            >>> state.col, state.row
            (2, 2)
            >>> state = state.up()
            >>> state.col, state.row
            (1, 2)
        """
        self._move_cursor(distance * -1, 0)
        return self

    def update_ui(self) -> None:
        """Draw the UI for the edit state.

        :returns: `None`.
        :rtype: NoneType
        """
        super().update_ui()
        self._draw_cursor()


class End(State):
    """A state that terminates the game of life.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.End` object.
    :rtype: life.sui.End

    Usage::

        >>> from life.life import Grid
        >>> from blessed import Terminal
        >>>
        >>> grid = Grid(5, 5)
        >>> term = Terminal()
        >>> state = End(grid, term)
        >>> type(state)
        <class 'life.sui.End'>
    """
    def input(self) -> Command:
        """This should never be called on an End object. It will
        raise a :class:`life.sui.CannotTakeInput` error if ever
        called.

        :returns: A :class:`Command` object
        :rtype: Command
        """
        raise CannotTakeInput('End objects do not get input.')
        return tuple()

    def update_ui(self) -> None:
        """Do not change the UI.

        :returns: `None`.
        :rtype: NoneType
        """
        pass


class Load(State):
    """The state for loading patterns from a file.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Load` object.
    :rtype: life.sui.Load

    Usage::

        >>> from life.life import Grid
        >>> from blessed import Terminal
        >>>
        >>> grid = Grid(5, 5)
        >>> term = Terminal()
        >>> state = Load(grid, term)
        >>> type(state)
        <class 'life.sui.Load'>
    """
    commands = {
        DOWN: 'down',
        UP: 'up',
        'f': 'file',
        'x': 'exit',
        '\n': 'load',
    }
    _menu = '(\u2191\u2192) Move, (\u23ce) Select, (F)rom file, e(X)it'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.files: list[str] = []
        self.path = files(life.pattern)
        self.selected = 0

    # Private methods.
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

    # Public methods.
    def down(self) -> 'Load':
        """Command method. Select the next file in the list.

        :returns: A :class:`life.sui.Load`
        :rtype: life.sui.Load

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Load(grid, term)
            >>>
            >>> state._get_files()
            >>> state.selected
            0
            >>> state = state.down()
            >>> state.selected
            1
        """
        self.selected += 1
        self.selected = self.selected % len(self.files)
        return self

    def exit(self) -> 'Core':
        """Command method. Exit load state.

        :returns: A :class:`life.sui.Core`
        :rtype: life.sui.Core

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Load(grid, term)
            >>>
            >>> state = state.exit()
            >>> type(state)
            <class 'life.sui.Core'>
        """
        return Core(**self.asdict())

    def file(self, path: Path = Path.cwd()) -> 'Load':
        """Command method. Select from files in the current working
        directory.

        :param path: The path of the file to load.
        :returns: A :class:`life.sui.Load`
        :rtype: life.sui.Load

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>> from pathlib import Path
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Load(grid, term)
            >>> state.path = Path('/')
            >>>
            >>> state.path
            PosixPath('/')
            >>> state = state.file(Path('/tmp'))
            >>> state.path
            PosixPath('/tmp')
        """
        self.path = path
        return self

    def load(
        self, filename: str | Path | Traversable | None = None
    ) -> Union['Core', 'Load']:
        """Load the selected file and return to core state.

        :param path: The path of the file to load.
        :returns: A :class:`life.sui.Load`
        :rtype: life.sui.Load
        """
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
                raw = fh.read()
            if filename.suffix == '.cells':
                normal, info = decode(raw, 'cells')
            elif filename.suffix == '.rle':
                normal, info = decode(raw, 'rle')
            else:
                normal, info = decode(raw, 'pattern')
            self.data.replace(normal)
            self.user = info.user
            self.comment = info.comment

        self.data.generation = 0
        return Core(**self.asdict())

    def up(self) -> 'Load':
        """Command method. Select the previous file in the list.

        :returns: A :class:`life.sui.Load`
        :rtype: life.sui.Load

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Load(grid, term)
            >>> state._get_files()
            >>> state.selected = 1
            >>>
            >>> state.selected
            1
            >>> state = state.up()
            >>> state.selected
            0
        """
        self.selected -= 1
        self.selected = self.selected % len(self.files)
        return self


class Move(State):
    """The state for moving the window on the grid.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Move` object.
    :rtype: life.sui.Move

    Usage::

        >>> from life.life import Grid
        >>> from blessed import Terminal
        >>>
        >>> grid = Grid(5, 5)
        >>> term = Terminal()
        >>> state = Move(grid, term)
        >>> type(state)
        <class 'life.sui.Move'>
    """
    commands = {
        DOWN: ('down', 1),
        LEFT: ('left', 1),
        RIGHT: ('right', 1),
        UP: ('up', 1),
        SDOWN: ('down', 10),
        SLEFT: ('left', 10),
        SRIGHT: ('right', 10),
        SUP: ('up', 10),
        'x': 'exit',
    }
    _menu = '(\u2190\u2191\u2192\u2193) Move, e(X)it'

    def down(self, distance: int = 1) -> 'Move':
        """Command method. Move the window down.

        :param distance: (Optional.) How far to move. Defaults to `1`.
        :returns: An :class:`life.sui.Move` object.
        :rtype: life.sui.Move

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Move(grid, term)
            >>>
            >>> state.origin_x, state.origin_y
            (-38, -55)
            >>> state = state.down(1)
            >>> state.origin_x, state.origin_y
            (-38, -109)
        """
        self.origin_y += distance
        if self.origin_y > (self.data.height - (self.term.height - 3) * 2):
            self.origin_y = (self.data.height - (self.term.height - 3) * 2)
        return self

    def exit(self) -> 'Core':
        """Command method. Return to the core.

        :returns: An :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Move(grid, term)
            >>>
            >>> state = state.exit()
            >>> type(state)
            <class 'life.sui.Core'>
        """
        return Core(**self.asdict())

    def left(self, distance: int = 1) -> 'Move':
        """Command method. Move the window left.

        :param distance: (Optional.) How far to move. Defaults to `1`.
        :returns: An :class:`life.sui.Move` object.
        :rtype: life.sui.Move

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Move(grid, term)
            >>>
            >>> state.origin_x, state.origin_y
            (-38, -55)
            >>> state = state.left(1)
            >>> state.origin_x, state.origin_y
            (0, -55)
        """
        self.origin_x -= distance
        if self.origin_x < 0:
            self.origin_x = 0
        return self

    def right(self, distance: int = 1) -> 'Move':
        """Command method. Move the window right.

        :param distance: (Optional.) How far to move. Defaults to `1`.
        :returns: An :class:`life.sui.Move` object.
        :rtype: life.sui.Move

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Move(grid, term)
            >>>
            >>> state.origin_x, state.origin_y
            (-38, -55)
            >>> state = state.right(1)
            >>> state.origin_x, state.origin_y
            (-75, -55)
        """
        self.origin_x += distance
        if self.origin_x > (self.data.width - self.term.width):
            self.origin_x = self.data.width - self.term.width
        return self

    def up(self, distance: int = 1) -> 'Move':
        """Command method. Move the window up.

        :param distance: (Optional.) How far to move. Defaults to `1`.
        :returns: An :class:`life.sui.Move` object.
        :rtype: life.sui.Move

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Move(grid, term)
            >>>
            >>> grid = Grid(5, 5)
            >>> state = Move(grid, term)
            >>>
            >>> state.origin_x, state.origin_y
            (-38, -55)
            >>> state = state.up(1)
            >>> state.origin_x, state.origin_y
            (-38, 0)
        """
        self.origin_y -= distance
        if self.origin_y < 0:
            self.origin_y = 0
        return self


class Save(State):
    """The state for saving the grid state to a file.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Save` object.
    :rtype: life.sui.Save

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Save(grid, term)
            >>> type(state)
            <class 'life.sui.Save'>
    """
    _menu = 'Enter name for save file.'
    path = Path('')

    def exit(self) -> 'Core':
        """Command method. Return to core without saving.

        :returns: An :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Save(grid, term)
            >>>
            >>> state = state.exit()
            >>> type(state)
            <class 'life.sui.Core'>
        """
        return Core(**self.asdict())

    def input(self) -> Command:
        """Get a file name from the user.

        :returns: A :class:`tuple` object.
        :rtype: tuple
        """
        self._draw_prompt()
        y = -(self.data.height // -2) + 2

        result = self._get_text(y, 2, is_path=True)
        if result == ESC:
            return ('exit',)
        return ('save', result)

    def save(self, filename: str | Path) -> 'Core':
        """Save the current grid state to a file.

        :param filename: The name of the file to save.
        :returns: An :class:`life.sui.Core` object.
        :rtype: life.sui.Core
        """
        path = Path(filename)
        info = util.FileInfo(
            path.name, self.user, self.data.rule, self.comment
        )
        text = encode(self.data.view(), self.save_format, info)
        if '/' not in str(filename):
            path = self.path / filename
        with open(path, 'w') as fh:
            fh.write(text)
        return Core(**self.asdict())


class Start(State):
    """The starting state for the UI, displaying the title screen.

    :param data: The grid object for the current Game of Life.
    :param term: The terminal the Game of Life is being run in.
    :param origin_x: (Optional.) The X location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param origin_y:  (Optional.) The Y location for the upper-left
        corner of the displayed area of the grid. Defaults to `None`.
    :param pace: The time between ticks in the game. Defaults to `0`.
    :param show_generation: Whether to display the generation of
        the Game of Life. Defaults to `False`.
    :param user: The name of the user to credit in save files.
        Defaults to an empty `str`.
    :param comment: A comment for the save file. Defaults to an
        empty `str`.
    :param save_format: The format to use when saving the file.
        Defaults to `cells`.
    :returns: An :class:`life.sui.Start` object.
    :rtype: life.sui.Start

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Start(grid, term)
            >>>
            >>> state = state.exit()
            >>> type(state)
            <class 'life.sui.Start'>
    """
    _menu = 'Copyright © 2020 Paul J. Iutzi'
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

    # Public methods.
    def input(self) -> Command:
        """Get input from the user.

        :returns: A :class:`tuple` object.
        :rtype: tuple
        """
        self._draw_prompt(self.prompt)
        with self.term.cbreak():
            self.term.inkey()
        return ('run',)

    def run(self) -> Core:
        """Return a Core object to start the game of life.

        :returns: An :class:`life.sui.Core` object.
        :rtype: life.sui.Core

        Usage::

            >>> from life.life import Grid
            >>> from blessed import Terminal
            >>>
            >>> grid = Grid(5, 5)
            >>> term = Terminal()
            >>> state = Start(grid, term)
            >>>
            >>> state = state.run()
            >>> type(state)
            <class 'life.sui.Core'>
        """
        return Core(**self.asdict())
