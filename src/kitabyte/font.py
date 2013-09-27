# encoding=utf8
'''Font data structures'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.


class Glyph(object):
    def __init__(self, char_code):
        '''Represents an individual glyph.'''
        self._char_code = char_code
        self.args = []
        self._pointmap = []
        self.line_number = None

    @property
    def bitmap(self):
        return self._pointmap

    @property
    def pointmap(self):
        '''Represents the points within the glyph.

        This map is a list of strings.
        '''
        return self._pointmap

    @property
    def char_code(self):
        '''The Unicode integer of the glyph.'''
        return self._char_code

    def clean_pointmap(self):
        '''Removes extraneous whitespace and lines.'''
        # Trim whitespace on the right
        for i in xrange(len(self._pointmap)):
            point_list = self._pointmap[i]
            line = u''.join(point_list).rstrip()
            self._pointmap[i] = list(line)

        # Delete empty lines starting from the bottom
        for i in xrange(len(self._pointmap) - 1, 0, -1):
            if self._pointmap[i]:
                break

            del self._pointmap[i]
