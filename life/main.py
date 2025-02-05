"""
main
~~~~

Main program loop for :mod:`life`.
"""
from argparse import ArgumentParser

from life.sui import main_loop


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
        type=float,
        default=0.0
    )
    p.add_argument(
        '-r', '--rule',
        help='The rule for the Game of Life.',
        action='store',
        type=str,
        default='b3/s23'
    )
    p.add_argument(
        '-W', '--no_wrap',
        help='The grid should not wrap at the edges.',
        action='store_true'
    )
    args = p.parse_args()

    file = args.file.strip() if args.file else ''
    rule = args.rule.strip() if args.rule else args.rule
    main_loop(
        dimensions=args.dimensions,
        file=file,
        show_generation=args.show_generation,
        pace=args.pace,
        rule=rule,
        no_wrap=args.no_wrap
    )
