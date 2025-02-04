"""
life
~~~~

A simple implementation of Conway's Game of Life.
"""
from collections import Counter
from collections.abc import Iterator, Sequence
from itertools import chain, product
from re import search

import numpy as np
from numpy.typing import NDArray

from life import util
from life.model import LifeAry


# Types.
Boollike = bool | int
Gridlike = Sequence[Sequence[Boollike]]


# Exceptions.
class InvalidRule(ValueError):
    """The given rule is not properly formatted."""


class PartialImplentation(Exception):
    """Grid doesn't fully implement MutableSequence.'"""


# Classes.
class Grid:
    """A grid for the Game of Life.

    :param width: The number of positions in the width of the grid.
    :param height: The number of positions in the height of the grid.
    :param rule: (Optional.) The rules for the Game of Life as a
        :class:`str`. It follows the pattern `B[0-8]*[/]S[0-8]*` where
        `B` is the numbers of adjacent live squares needed for the current
        square to be born and `S` is the numbers of adjacent live squares
        needed for a live square to stay alive. It defaults to `B3/S23`.
    :returns: A :class:`life.life.Grid` object.
    :rtype: life.life.Grid

    Usage::

        >>> # To create an 10x12 grid for the Game of Life, using the
        >>> # standard rules.
        >>> grid = Grid(10, 12, 'b3/s23')
        >>> grid
        Grid(10, 12, 'b3/s23')
    """
    rng = np.random.default_rng()

    # Class methods.
    @classmethod
    def from_array(cls, a: LifeAry, rule: str = 'B3/S23') -> 'Grid':
        """Build a new :class:`Grid` from a :class:`numpy.ndarray`.

        :param a: The array used to build the :class:`life.life.Grid`.
        :param rule: (Optional.) The rules for the Game of Life as a
            :class:`str`. It follows the pattern `B[0-8]+[/]S[0-8]+` where
            `B` is the numbers of adjacent live squares needed for the current
            square to be born and `S` is the numbers of adjacent live squares
            needed for a live square to stay alive. It defaults to `B3/S23`.
        :returns: A :class:`life.life.Grid` object.
        :rtype: life.life.Grid

        Usage::

            >>> a = np.array([
            ...     [False, True, False, True],
            ...     [True, False, True, False],
            ...     [False, True, False, True],
            ...     [True, False, True, False],
            ... ])
            >>> grid = Grid.from_array(a, 'b3/s23')
            >>> grid
            Grid(4, 4, 'b3/s23')
            >>> str(grid)
            '.X.X\nX.X.\n.X.X\nX.X.'
        """
        height, width = a.shape
        grid = cls(width, height, rule)
        grid._data = a
        return grid

    # Initialization.
    def __init__(
        self, width: int,
        height: int,
        rule: str = 'B3/S23', wrap: bool = True
    ) -> None:
        """Initialize an instance of the class."""
        self.height = height
        self.rule = rule
        self.width = int(width)
        self.wrap = wrap

        self.generation = 0
        self._data: np.ndarray = np.zeros(
            (self.height, self.width),
            dtype=bool
        )

    # Rule properties.
    @property
    def born(self) -> tuple[int, ...]:
        """The numbers of neighbors that cause a cell to be born.

        :returns: A :class:`tuple` object.
        :rtype: tuple

        Usage::

            >>> grid = Grid(10, 12, 'b3/s23')
            >>> grid.born
            (3,)
        """
        return self._born

    @property
    def rule(self) -> str:
        """The rules for the Game of Life.

        :returns: A :class:`str` object.
        :rtype: str

        Usage::

            >>> grid = Grid(10, 12, 'b3/s23')
            >>> grid.rule
            'b3/s23'
        """
        return self._rule

    @rule.setter
    def rule(self, value: str) -> None:
        """The rules for the Game of Life.

        :param value: (Optional.) The rules for the Game of Life as a
            :class:`str`. It follows the pattern `B[0-8]+[/]S[0-8]+` where
            `B` is the numbers of adjacent live squares needed for the current
            square to be born and `S` is the numbers of adjacent live squares
            needed for a live square to stay alive. It defaults to `B3/S23`.
        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> grid = Grid(10, 12, 'b3/s23')
            >>> grid.rule = 'b2/s45'
            >>> grid.rule
            'b2/s45'
        """
        # Validate rule string.
        if not search(r'^[bB][0-9]*[/][sS][0-9]*$', value):
            raise InvalidRule('Invalid rule format.')

        # Parse rule string.
        born_str, survive_str = value.split('/')
        born = [int(n) for n in born_str[1:]]
        survive = [int(n) for n in survive_str[1:]]
        self._rule = value
        self._born = tuple(born)
        self._survive = tuple(survive)

    @property
    def survive(self) -> tuple[int, ...]:
        """The numbers of neighbors that cause a cell to survive.

        :returns: A :class:`tuple` object.
        :rtype: tuple

        Usage::

            >>> grid = Grid(10, 12, 'b3/s23')
            >>> grid.survive
            (2, 3)
        """
        return self._survive

    # Properties.
    @property
    def shape(self) -> tuple[int, ...]:
        """The dimensions of the :class:`life.life.Grid`.

        :returns: A :class:`tuple` object.
        :rtype: tuple

        Usage::

            >>> grid = Grid(10, 12, 'b3/s23')
            >>> grid.shape
            (12, 10)
        """
        return self._data.shape

    # Comparisons.
    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        try:
            return (
                (self._data == other._data).all()
                and self.rule == other.rule
            )
        except ValueError:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    # Representations.
    def __repr__(self) -> str:
        name = type(self).__name__
        return f'{name}({self.width}, {self.height}, {self.rule!r})'

    def __str__(self) -> str:
        a: np.ndarray = np.ndarray(self._data.shape, dtype='<U1')
        a.fill('X')
        a[~self._data] = '.'
        return '\n'.join(''.join(c for c in row) for row in a)

    # MutableSequence protocol (partial).
    def __delitem__(self, key) -> None:
        raise PartialImplentation('Locations in a Grid cannot be deleted.')

    def __iadd__(self, value) -> None:
        raise PartialImplentation(
            'Locations cannot be added incrementally to a Grid.'
        )

    def __setitem__(self, key, value) -> None:
        return self._data.__setitem__(key, value)

    def insert(self, key, value) -> None:
        raise PartialImplentation('Locations cannot be inserted into a Grid.')

    def pop(self, key) -> bool:
        raise PartialImplentation('Locations cannot be popped from a Grid.')

    def remove(self, key) -> None:
        raise PartialImplentation('Locations cannot be removed from a Grid.')

    # Sequence protocol.
    def __contains__(self, item) -> bool:
        return item in self._data

    def __getitem__(self, key) -> bool:
        return self._data.__getitem__(key)

    def __iter__(self) -> Iterator[LifeAry]:
        while True:
            self.tick()
            yield self._data

    def __len__(self) -> int:
        return len(self._data)

    def __reversed__(self) -> Iterator[LifeAry]:
        a = self._data.copy()
        a = np.flip(a, axis=0)
        a = np.flip(a, axis=1)
        for row in a:
            for item in row:
                yield item

    def count(self, value) -> int:
        counts = Counter(self._data.ravel())
        return counts[value]

    def index(self, value) -> tuple[int, int]:
        for y, row in enumerate(self._data):
            for x, item in enumerate(row):
                if item == value:
                    return (y, x)
        raise ValueError(f'{value} not in grid.')

    # Method to manage the Game of Life.
    def clear(self) -> None:
        """Clear all live locations from the grid.

        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> a = np.array([
            ...     [False, True, False, True],
            ...     [True, False, True, False],
            ...     [False, True, False, True],
            ...     [True, False, True, False],
            ... ])
            >>> grid = Grid.from_array(a, 'b3/s23')
            >>> str(grid)
            '.X.X\nX.X.\n.X.X\nX.X.'
            >>> grid.clear()
            >>> str(grid)
            '....\n....\n....\n....'
        """
        self._data.fill(False)

    def flip(self, x: int, y: int) -> None:
        """Change the value of the given location on the
        :class:`life.life.Grid` to its opposite value.

        :param x: The X axis position of the location to change.
        :param y: The Y axis position of the location to change.
        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> grid = Grid(4, 4)
            >>> str(grid)
            '....\n....\n....\n....'
            >>> grid.flip(1, 2)
            >>> str(grid)
            '....\n....\n.X..\n....'
        """
        value = (self._data[y][x] + 1) % 2
        self._data[y][x] = value

    def randomize(self) -> None:
        """Randomize the values of the grid.

        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> grid = Grid(5, 5)
            >>>
            >>> # This line is just to seed the random number generator
            >>> # to ensure repeatability for testing the documentation.
            >>> # Do not do this is you want randomization.
            >>> grid.rng = np.random.default_rng(1138)
            >>>
            >>> print(grid)
            .....
            .....
            .....
            .....
            .....
            >>> grid.randomize()
            >>> print(grid)
            ..XX.
            .XX.X
            X.X.X
            ..XX.
            XX...
        """
        new = self.rng.integers(0, 2, self.shape, dtype=bool)
        self._data = new

    def replace(self, seq: Gridlike | LifeAry) -> None:
        """Replace the :class:`life.life.Grid` with the given values.

        :param seq: An array or similar two-dimensional sequence with
            values to use when replacing the current :class:`life.life.Grid`
            values.
        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> grid = Grid(5, 5)
            >>> a = np.array([
            ...     [False, False, False, False, False],
            ...     [False, True, True, True, False],
            ...     [False, False, False, True, False],
            ...     [False, False, True, False, False],
            ...     [False, False, False, False, False],
            ... ])
            >>>
            >>> print(grid)
            .....
            .....
            .....
            .....
            .....
            >>> grid.replace(a)
            >>> print(grid)
            .....
            .XXX.
            ...X.
            ..X..
            .....
        """
        try:
            new = np.array(seq, dtype=bool)
        except ValueError:
            raise ValueError(tuple(len(row) for row in seq))
        self._data = util.fit_array(new, self.shape)

    def tick(self) -> None:
        """Advance the Game of Life one generation.

        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> a = np.array([
            ...     [False, False, False, False, False],
            ...     [False, True, True, True, False],
            ...     [False, False, False, True, False],
            ...     [False, False, True, False, False],
            ...     [False, False, False, False, False],
            ... ])
            >>> grid = Grid.from_array(a)
            >>> print(grid)
            .....
            .XXX.
            ...X.
            ..X..
            .....
            >>> grid.tick()
            >>> print(grid)
            ..X..
            ..XX.
            .X.X.
            .....
            .....
            >>> grid.tick()
            >>> print(grid)
            ..XX.
            .X.X.
            ...X.
            .....
            .....
        """
        a = np.zeros(self.shape, dtype=int)

        # Set up for the roll.
        shifts = [shift for shift in product([-1, 0, 1], repeat=2)]
        shifts.remove((0, 0))
        Y, X = 0, 1

        # Perform the roll.
        for y_shift, x_shift in shifts:
            # Roll the array in the given direction along the given axis.
            b = np.roll(self._data, y_shift, Y)
            b = np.roll(b, x_shift, X)

            # If values shouldn't wrap, set the values of what did wrap
            # to zero.
            if not self.wrap and y_shift != 0:
                if y_shift == 1:
                    b[0, :] = np.zeros((b.shape[X],), dtype=bool)
                b[-1, :] = np.zeros((b.shape[X],), dtype=bool)
            if not self.wrap and x_shift != 0:
                if x_shift == 1:
                    b[:, 0] = np.zeros((b.shape[Y],), dtype=bool)
                b[:, -1] = np.zeros((b.shape[Y],), dtype=bool)

            # Add to the cumulative total.
            a += b

        # Apply the rules.
        keeps = set((*self.born, *self.survive))
        gones = [n for n in range(9) if n not in keeps]
        for n in gones:
            a[a == n] = 0
        a[self._data > 0] *= -1
        for n in self.born:
            a[a == n] = 9
        for n in self.survive:
            a[a == -n] = 9
        a[a < 9] = 0
        a[a == 9] = 1
        self._data = np.array(a, dtype=bool)
        self.generation += 1

    def view(
        self,
        origin: Sequence[int] = (0, 0),
        shape: Sequence[int] | None = None
    ) -> LifeAry:
        """Return a section of the data of the current grid.

        :param origin: The grid position of the upper-left corner of
            the view.
        :param shape: The X and Y dimensions of the view.
        :returns: A :class:`numpy.ndarray` object.
        :rtype: numpy.ndarray

        Usage::

            >>> a = np.array([
            ...     [False, False, False, False, False],
            ...     [False, True, True, True, False],
            ...     [False, False, False, True, False],
            ...     [False, False, True, False, False],
            ...     [False, False, False, False, False],
            ... ])
            >>> grid = Grid.from_array(a)
            >>> grid.view()
            array([[False, False, False, False, False],
                   [False,  True,  True,  True, False],
                   [False, False, False,  True, False],
                   [False, False,  True, False, False],
                   [False, False, False, False, False]])
        """
        if shape is None:
            shape = self._data.shape
        starty, startx = origin
        leny, lenx = shape
        stopy = starty + leny
        stopx = startx + lenx
        return self._data[starty:stopy, startx:stopx]
