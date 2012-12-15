# encoding=utf8
'''Font data structures'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.


class Glyph(object):
    def __init__(self, char_code):
#        self._bitmap = []
        self._char_code = char_code
        self.args = []
        self._pointmap = []
        self.line_number = None

    @property
    def bitmap(self):
        return self._pointmap

    @property
    def pointmap(self):
        return self._pointmap

    @property
    def char_code(self):
        return self._char_code

    def clean_pointmap(self):
        for i in xrange(len(self._pointmap)):
            point_list = self._pointmap[i]
            line = u''.join(point_list).rstrip()
            self._pointmap[i] = list(line)

        for i in xrange(len(self._pointmap) - 1, 0, -1):
            if self._pointmap[i]:
                break

            del self._pointmap[i]
