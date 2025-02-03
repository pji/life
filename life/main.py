"""
main
~~~~

Main program loop for :mod:`life`.
"""
from argparse import ArgumentParser

from blessed import Terminal

from life.life import Grid
from life.sui import End, Start


# Mainline.
def main() -> None:
    """Parse the arguments used to invoke :mod:`life` and run the script.

    :returns: `None`.
    :rtype: NoneType
    """
    # Parse the command line.
    p = ArgumentParser(
        description='A Python implementation of Conway\'s Game of Life.',
        prog='life'
    )
    p.add_argument(
        '-d', '--dimensions',
        help='The dimensions for the grid of the Game of Life.',
        action='store',
        nargs=2,
        type=int
    )
    p.add_argument(
        '-f', '--file',
        help='A file to load into the Game of Life.',
        action='store',
        type=str
    )
    p.add_argument(
        '-g', '--show_generation',
        help='Show the current generation during the Game of Life.',
        action='store_true'
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

    # Switch the terminal into a more interactive mode.
    term = Terminal()
    with term.fullscreen(), term.hidden_cursor():

        # Build the configuration.
        kwargs = {
            'term': term,
            'show_generation': args.show_generation,
        }
        if args.dimensions:
            kwargs['data'] = Grid(*args.dimensions)
        if args.file:
            kwargs['file'] = args.file.strip()
        if args.no_wrap:
            kwargs['wrap'] = False
        if args.pace:
            kwargs['pace'] = args.pace
        if args.rule:
            kwargs['rule'] = args.rule.strip()

        # Configure and run the Game of Life.
        state = Start(**kwargs)
        while not isinstance(state, End):
            state.update_ui()
            cmd, *cmd_args = state.input()
            state = getattr(state, cmd)(*cmd_args)
