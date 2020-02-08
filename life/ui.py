"""
ui
~~

The user interface for Conway's Game of Life.
"""
from collections import OrderedDict
from os.path import exists, isfile
import traceback as tb
from typing import List

from blessed import Terminal

from life.grid import Grid


class _Input:
    """A class for trusted input objects."""
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = self._validate(value)


class _Command(_Input):
    """A trusted object to handle command input from the UI."""
    valid = OrderedDict((
        ('c', 'clear'),
        ('e', 'edit'),
        ('l', 'load'),
        ('n', 'next'),
        ('q', 'quit'),
        ('r', 'random'),
    ))
    
    def __init__(self, value: str) -> None:
        self.default = 'n'
        self.value = value
    
    def _validate(self, value:str) -> str:
        normal = value.lower()
        if normal not in self.valid:
            normal = self.default
        return self.valid[normal]
    
    @classmethod
    def get_commands(cls) -> List[str]:
        """Return a list of available commands for display."""
        cmds = []
        for key in cls.valid:
            index = cls.valid[key].index(key)
            cmd = (f'{cls.valid[key][0:index]}({key.upper()})'
                   f'{cls.valid[key][index + 1:]}')
            cmds.append(cmd)
        return cmds


class _CursorNav(_Input):
    """A trusted object to handle cursor navigation input."""
    valid = OrderedDict((
        ('a', '(a) Left'),
        ('d', '(d) Right'), 
        ('w', '(w) Up'), 
        ('s', '(s) Down'),
        (' ', '(\u2420) Flip'),
        ('e', '(E)xit'),
    ))
    default = 'e'
    
    def __init__(self, value:str):
        self.value = value
    
    def _validate(self, value):
        normal = value.lower()
        if normal not in self.valid:
            normal = self.default
        return normal


class _LoadFile(_Input):
    """A trusted object to handle file name input from the UI."""
    def __init__(self, value: str, path: str = 'pattern/') -> None:
        self.path = path
        self.value = value
    
    def _validate(self, value):
        path = f'{self.path}{value}'
        if exists(path) and isfile(path):
            return path
        msg = 'File not found in pattern/'
        raise ValueError(msg)


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
            data = Grid(term.width, (term.height - 3) * 2)
        self.data = data
        self.cell_alive = '\u2588'
        self.cell_dead = ' '
    
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
    
    def _convert_text_pattern(self, text:str, live: str = 'x') -> list:
        """Convert a pattern saved as a text file into grid data.
        
        :param text: The pattern as text.
        :param live: The character that represents an alive cell.
        :return: The pattern converted to a table of True and False 
            values.
        :rtype: list
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
    
    def _draw_commands(self, cmds: list = None):
        """Draw the available commands."""
        if not cmds:
            cmds = _Command.get_commands()
        y = -(self.data.height // -2) + 1
        print(self.term.move(y, 0) + ' ' * self.term.width)
        print(self.term.move(y, 0) + ', '.join(cmds))
    
    def _draw_grid(self):
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
    
    def _get_filename(self, msg:str):
        """Prompt the use for the name of a file and return it.
        
        :param msg: The message to prompt the user with.
        :return: None
        :rtype: NoneType
        """
        self._draw_prompt(f'{msg} > ')
        x = len(msg) + 3
        y = -(self.data.height // -2) + 2
        resp = _LoadFile(input(self.term.move(y, x)))
        return resp
    
    def clear(self):
        """Clear all cell statuses from the grid."""
        self.data.clear()
        self.draw()
    
    def draw(self):
        """Draw the user interface."""
        self._draw_grid()
        self._draw_rule()
        self._draw_commands()
    
    def _draw_cursor(self, row, col):
        y = row // 2
        
        # Figure out whether either of the cells sharing the location 
        # are alive.
        alive = []
        char = ''
        if row % 2:
            alive.append(self.data[row - 1][col])
            alive.append(self.data[row][col])
            char = '\u2584'
        else:
            alive.append(self.data[row][col])
            alive.append(self.data[row + 1][col])
            char = '\u2580'
        
        # Figure out which character and color is needed for the 
        # cursor. The cursor will be green if on a dead cell and 
        # bright green if on a live cell. However, whether the 
        # colors or foreground or background gets complicated 
        # when both cells in the location are alive.
        if alive == [False, False]:
            color = self.term.green_on_black
        elif alive == [True, True]:
            color = self.term.bright_green_on_bright_white
        elif alive == [True, False] and not row % 2:
            color = self.term.bright_green_on_black
        elif alive == [True, False]:
            color = self.term.green_on_bright_white
        elif alive == [False, True] and not row % 2:
            color = self.term.green_on_bright_white
        else:
            color = self.term.bright_green_on_black
        
        print(self.term.move(y, col) + color + char 
              + self.term.bright_white_on_black)
        
    def edit(self):
        """Edit the grid through the UI."""
        cmds = (_CursorNav.valid[key] for key in _CursorNav.valid)
        self._draw_commands(cmds)
        row = self.data.height // 2
        col = self.data.width // 2
        with self.term.cbreak():
            while True:
                self._draw_cursor(row, col)
                cmd = _CursorNav(self.term.inkey())
                if cmd.value == 'a':
                    col -= 1
                elif cmd.value == 'd':
                    col += 1
                elif cmd.value == 'w':
                    row -= 1
                elif cmd.value == 's':
                    row += 1
                elif cmd.value == 'e':
                    break
                elif cmd.value == ' ':
                    self.data.flip(row, col)
                col = col % self.data.width
                self._draw_grid()
        self.draw()
    
    def input(self):
        """Get input from the user."""
        self._draw_prompt()
        with self.term.cbreak():
            cmd = _Command(self.term.inkey())
        return cmd
    
    def load(self, filename: str = None):
        """Load a GoL state from a file."""
        if not filename:
            filename = self._get_filename('Load file named')
        text = []
        with open(filename.value, 'r') as f:
            text = f.readlines()
        new = self._convert_text_pattern(text)
        self.data.replace(new)
        self.draw()
    
    def next(self):
        """Advance the generation of the grid and draw the results."""
        self.data.next_generation()
        self.draw()
    
    def random(self):
        """Randomize the values of the cells in the grid."""
        self.data.randomize()
        self.draw()


def main(ctlr: TerminalController = None) -> None:
    if not ctlr:
        ctlr = TerminalController()
    with ctlr.term.fullscreen(), ctlr.term.hidden_cursor():
        ctlr.load(_LoadFile('title.txt'))
        ctlr.draw()
        while True:
            cmd = ctlr.input()
            if cmd.value == 'quit':
                break
            getattr(ctlr, cmd.value)()
            

if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        with open('exception.log', 'w') as fh:
            fh.write(str(ex.args))
            tb_str = ''.join(tb.format_tb(ex.__traceback__))
            fh.write(tb_str)
        raise ex