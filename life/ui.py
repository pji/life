"""
ui
~~

The user interface for Conway's Game of Life.
"""
from os.path import exists, isfile
import traceback as tb

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
    def __init__(self, value: str) -> None:
        self.valid = {
            'c': 'clear',
            'l': 'load',
            'n': 'next',
            'q': 'quit',
            'r': 'random',
        }
        self.default = 'n'
        self.value = value
    
    def _validate(self, value):
        normal = value.lower()
        if normal not in self.valid:
            normal = self.default
        self._value = self.valid[normal]


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
#             data = Grid((term.height - 3) * 2, term.width)
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
    
    def _draw_commands(self):
        """Draw the available commands."""
        cmds = ['(C)lear', '(L)oad', '(N)ext', '(R)andom', '(Q)uit',]
        y = -(self.data.height // -2) + 1
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
    
    def next(self):
        """Advance the generation of the grid and draw the results."""
        self.data.next_generation()
        self.draw()
    
    def input(self):
        """Get input from the user."""
        self._draw_prompt()
        with self.term.cbreak():
            cmd = _Command(self.term.inkey())
        return cmd
    
    def load(self):
        """Load a GoL state from a file."""
        filename = self._get_filename('Load file named')
        text = []
        with open(filename.value, 'r') as f:
            text = f.readlines()
        new = self._convert_text_pattern(text)
        self.data.replace(new)
        self.draw()
    
    def random(self):
        """Randomize the values of the cells in the grid."""
        self.data.randomize()
        self.draw()


def main(ctlr: TerminalController = None) -> None:
    if not ctlr:
        ctlr = TerminalController()
    ctlr.data.randomize()
    with ctlr.term.fullscreen(), ctlr.term.hidden_cursor():
        ctlr.draw()
        while True:
            cmd = yield ctlr.input()
            getattr(ctlr, cmd.value)()
            

if __name__ == '__main__':
    loop = main()
    next(loop)
    cmd = _Command('n')
    try:
        while cmd.value != 'quit':
            cmd = loop.send(cmd)
    except Exception as ex:
        with open('exception.log', 'w') as fh:
            fh.write(str(ex.args))
            tb_str = ''.join(tb.format_tb(ex.__traceback__))
            fh.write(tb_str)
        loop.close()
        raise ex
    loop.close()