"""
ui
~~

The user interface for Conway's Game of Life.
"""
from blessed import Terminal

from life.grid import Grid


class _Command:
    """A trusted object to handle command input from the UI."""
    def __init__(self, value: str) -> None:
        self.valid = {
            'n': 'next',
            'q': 'quit',
            'r': 'random',
        }
        self.default = 'n'
        self.value = value
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        normal = value.lower()
        if normal not in self.valid:
            normal = self.default
        self._value = self.valid[normal]


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
    
    def _draw_commands(self):
        """Draw the available commands."""
        cmds = ['(N)ext', '(R)andom', '(Q)uit',]
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
    
    def _draw_prompt(self):
        """Draw the command prompt."""
        y = -(self.data.height // -2) + 2
        print(self.term.move(y, 0) + '> ')
    
    def _draw_rule(self):
        """Draw the a horizontal rule."""
        width = self.data.width
        y = -(self.data.height // -2)
        print(self.term.move(y, 0) + '\u2500' * width)
    
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
    while cmd.value == 'next':
        cmd = loop.send(cmd)
    loop.close()