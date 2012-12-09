# encoding=utf8
'''Font data structures'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.


class Glyph(object):
    def __init__(self, char_code):
        self._bitmap = []
        self._char_code = char_code

    @property
    def bitmap(self):
        return self._bitmap

    @property
    def char_code(self):
        return self._char_code
