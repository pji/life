"""
life
~~~~

A simple implementation of Conway's Game of Life.
"""
from collections import Counter
from collections.abc import Iterator, Sequence
from itertools import chain, product

import numpy as np
from numpy.typing import NDArray

from life import util


# Types.
Boollike = bool | int
Gridlike = Sequence[Sequence[Boollike]]


# Exceptions.
class PartialImplentation(Exception):
    """Grid doesn't fully implement MutableSequence.'"""


# Classes.
class Grid:
    rng = np.random.default_rng()

    # Class methods.
    @classmethod
    def from_array(cls, a: NDArray[np.bool_], rule: str = 'B3/S23') -> 'Grid':
        """Build a new :class:`Grid` from a :class:`numpy.ndarray`."""
        height, width = a.shape
        grid = cls(width, height, rule)
        grid._data = a
        return grid

    # Initialization.
    def __init__(
        self, width: int, height: int, rule: str = 'B3/S23'
    ) -> None:
        """Initialize an instance of the class."""
        self.height = height
        self.rule = rule
        self.width = int(width)

        self._data: np.ndarray = np.zeros(
            (self.height, self.width),
            dtype=bool
        )

    # Rule properties.
    @property
    def born(self) -> tuple[int, ...]:
        """The numbers of neighbors that cause a cell to be born."""
        return self._born

    @property
    def rule(self) -> str:
        """The rules for the Game of Life."""
        return self._rule

    @rule.setter
    def rule(self, value: str) -> None:
        """The rules for the Game of Life."""
        born_str, survive_str = value.split('/')
        born = [int(n) for n in born_str[1:]]
        survive = [int(n) for n in survive_str[1:]]
        self._rule = value
        self._born = tuple(born)
        self._survive = tuple(survive)

    @property
    def survive(self) -> tuple[int, ...]:
        """The numbers of neighbors that cause a cell to survive."""
        return self._survive

    # Properties.
    @property
    def shape(self) -> tuple[int, ...]:
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

    def __iter__(self) -> Iterator[NDArray[np.bool_]]:
        while True:
            self.tick()
            yield self._data

    def __len__(self) -> int:
        return len(self._data)

    def __reversed__(self) -> Iterator[NDArray[np.bool_]]:
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
        """Clear all live locations from the grid."""
        self._data.fill(False)

    def flip(self, x: int, y: int) -> None:
        """Change the valu of the given location on the :class:`Grid`
        to its opposite value.
        """
        value = (self._data[y][x] + 1) % 2
        self._data[y][x] = value

    def randomize(self) -> None:
        """Randomize the values of the grid."""
        new = self.rng.integers(0, 2, self.shape, dtype=bool)
        self._data = new

    def replace(self, seq: Gridlike) -> None:
        """Replace the :class:`Grid` with the given values."""
        new = np.array(seq, dtype=bool)
        self._data = util.fit_array(new, self.shape)

    def tick(self) -> None:
        """Advance the Game of Life one generation."""
        a = np.zeros(self.shape, dtype=int)

        # Set up for the roll.
        shifts = [shift for shift in product([-1, 0, 1], repeat=2)]
        shifts.remove((0, 0))
        Y, X = 0, 1

        # Perform the roll.
        for y_shift, x_shift in shifts:
            b = np.roll(self._data, y_shift, Y)
            b = np.roll(b, x_shift, X)
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
