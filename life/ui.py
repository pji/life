"""
ui
~~

The user interface for Conway's Game of Life.
"""
from blessed import Terminal

from life.grid import Grid


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
            data = Grid(term.width, term.height - 3)
        self.data = data
        self.cell_alive = '\u2588'
        self.cell_dead = ' '
    
    def _char_for_state(self, is_alive):
        """Return the character to draw based on the state of the cell."""
        if is_alive:
            return self.cell_alive
        else:
            return self.cell_dead
    
    def _draw_commands(self):
        """Draw the available commands."""
        cmds = ['(N)ext', '(R)andom', '(Q)uit',]
        y = self.data.height + 1
        print(self.term.move(y, 0) + ', '.join(cmds))
    
    def _draw_grid(self):
        """Draw the grid to the terminal."""
        for index in range(len(self.data)):
            cells = [self._char_for_state(cell) for cell in self.data[index]]
            print(self.term.move(index, 0) + ''.join(cells))
    
    def _draw_prompt(self):
        """Draw the command prompt."""
        y = self.data.height + 2
        print(self.term.move(y, 0) + '> ')
    
    def _draw_rule(self):
        """Draw the a horizontal rule."""
        width = self.data.width
        y = self.data.height
        print(self.term.move(y, 0) + '\u2500' * width)
    
    def draw(self):
        """Draw the user interface."""
        self._draw_grid()
        self._draw_rule()
        self._draw_commands()
        self._draw_prompt()


def main(ctlr:TerminalController = None) -> None:
    if not ctlr:
        ctlr = TerminalController()
#     ctlr.data.randomize()
    with ctlr.term.fullscreen(), ctlr.term.hidden_cursor():
        while True:
#             print(stlr.term.move(0, 0) + ctlr.data
            yield True
            
