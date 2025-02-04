====
life
====

Yet another implementation of Conway's Game of Life.


What is Conway's Game of Life?
------------------------------
Developed by John Horton Conway and first published in the October 
1970 issue of *Scientific American,* the Game of Life is a cellular 
automation that follows the following simple rules: 

1.  Any live cell with fewer than two live neighbors dies.
2.  Any live cell with two or three neighbors remains alive.
3.  Any live cell with more than three neighbors dies.
4.  Any dead cell with exactly three neighbors becomes alive.

From those simple rules, a great amount of interesting complexity 
arises.


Why implement Conway's Game of Life?
------------------------------------
There isn't any profound reason behind this. Back in 2007, I started 
learning Python. I had just learned about the Game if Life a few years 
before, and it seemed like a good project to use to help me explore 
how to solve problems with the language. And, lo, life became the 
second project I ever wrote in Python.

It's now 2020, and I've spent a lot more time with the language. I 
thought it might be fun to go back and reimplement the first few 
things I wrote in Python to see what I would do differently. Not that 
this implementation is necessarily any better. Sometimes experience 
helps you avoid mistakes. Sometimes experience helps you make even 
bigger ones. But, if nothing else, at least I write unit tests now.


How do I run the code?
----------------------
To run life, clone this repository to your local system and run the 
following from the repository::

    python3 -m life

That assumes you have Python 3.11 or greater installed as `python3`.


How do I use life?
------------------
When you first run life, you will see a title screen. At the bottom 
of the title screen, it says "Press any key to continue." Do so.

After you press any key, the text at the bottom of the screen will 
change to show you a list of commands. You press the key surrounded 
by parenthesis to use that command. For example, if you with to use 
the "(N)ext" command, press the 'n' key.

The initial commands available are:

* (A)utorun: automatically advance to the next generation until 
  stopped.
* (C)lear: turn all live cells to dead cells.
* (E)dit: Enter edit mode, where you can manually set which cells are 
  alive and dead.
* con(F)ig: Change configuration settings.
* (L)oad: load a saved pattern.
* (N)ext: advance to the next generation.
* (S)ave: save the current pattern.
* (Q)uit: quit this Game of Life.


How to run the tests?
---------------------
To run the tests, clone this repository to your local system and run 
the following from the root of the repository::

    python3 -m pytest

That assumes you have a fairly recent version of Python 3 available 
and it's at least aliased to `python3`.


Most Recent Changes
-------------------
The following features were added in the most recent release:

*   Removed warnings when tested under Python 3.13.
*   Switched from `pipenv` to `poetry`.
*   Added attributes to `life.sui.End` to better fit the base class.
*   Refactored `life.sui.State.update_ui` to increase code reuse.


To-do List
----------
The following features are still planned to be implemented:

*   Store user name in a configuration file.
*   Look at more efficient algorithms for GoL. (bitpack?, striding?)
*   Allow editing to increase and decrease brush size.
*   Allow editing to place -ominos.
*   Allow editing to place rotated -ominoes.
*   Allow editing to place agars.
*   Show previous generation as a different color.
*   Download patterns from URLs.
