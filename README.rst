Kitabyte Typeface
=================

.. image:: https://raw.github.com/chfoo/kitabyte/master/KitabyteRegularSpecimen.png
    :alt: Font specimen.

Kitabyte is a font family inspired by video game bitmap fonts and the
film Wreck-It Ralph. The font files are generated from text files.

* Launchpad Project Webpage (questions): https://launchpad.net/kitabyte
* GitHub Repo Webpage (bug reports): https://github.com/chfoo/kitabyte/ 
* Downloads: https://launchpad.net/kitabyte/+download


Building
========

To build the fonts, you will need:

1. Python 2.7
2. FontForge Python Scripting Extension

   * On Ubuntu, the package is called ``python-fontforge``.

A Makefile is provided.


Glyph definitions
=================

The glyph is defined by a beginning ``[`` then followed by the character
code in hexadecimal. Optional arguments are separated by spaces. Then,
the visual representation is defined by some ASCII art. A ``]`` marks
the end of the glyph.


Arguments
+++++++++

reference:u+XX
    Adds a linked glyph representation.

diacritic:u+XX
    Adds a diacritic to the glyph.

combining
    Gives the glyph zero width.


Anchor characters
+++++++++++++++++

====== ======= ==== ==========
Symbol Visible Type Class Name
====== ======= ==== ==========
t      true    base Top
T              base Top
p      true    mark Top
P              mark Top
b      true    base Bottom
B              base Bottom
m      true    mark Bottom
M              mark Bottom
====== ======= ==== ==========


Sizes
+++++

The glyphs are monospaced. Half-width glyphs fit within this grid::

     012345678
     1
     2
     3
     4
     5 ‾‾ascent
     6
     7 ‾‾x-height
     8
     9
    10
    11
    12 __baseline
    13
    14 __descent
    15
    16

Note that the various heights may vary among glyphs and the columns 1 and 8 are usually empty for spacing.
