Kitabyte Typeface
=================

Kitabyte is a font family inspired by video game bitmap fonts. The font
files are generated from text files.

Project webpage: https://launchpad.net/kitabyte


Building
========

To build the fonts, you will need:

1. Python 2.7
2. FontForge Python Scripting Extension

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

Anchor characters
+++++++++++++++++

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

