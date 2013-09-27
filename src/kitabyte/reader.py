# encoding=utf8
'''Text file reader'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
from __future__ import print_function
from kitabyte.font import Glyph
import glob
import os.path


class Comment(object):
    '''Represents a comment in the definition.'''
    def __init__(self, text):
        self.text = text


class Reader(object):
    '''A wrapper to multiple files.'''
    def __init__(self, *filenames):
        self._filenames = filenames
        self._index = -1
        self._filename = None
        self._file = None
        self._line_number = 0
        self._line = None

        self._open_next_file()
        self._read_next_line()

    def _open_next_file(self):
        '''Increment the index and open the next file.'''
        self._index += 1

        if len(self._filenames) <= self._index:
            self._file = None
            return

        self._line_number = 0
        self._filename = self._filenames[self._index]
        self._file = open(self._filename, 'r')

    def _read_next_line(self):
        '''Read and save the current line.'''
        if not self._file:
            return

        line = self._file.readline()

        if not line:
            self._line = None
            self._open_next_file()
            self._read_next_line()
            return

        self._line_number += 1
        self._line = line.rstrip('\n')

    def peek(self):
        '''Returns the next unread line without advancing to next line.'''
        return self._line

    def line(self):
        '''Returns the next unread line.'''
        line = self._line

        self._read_next_line()

        return line

    @property
    def line_number(self):
        '''Returns the current line number.'''
        return self._line_number

    @property
    def filename(self):
        '''Returns the current path of the file.'''
        return self._filename


def read_glyph(reader, char_code, args):
    '''Parses the point map definition into a Glyph object.'''
    glyph = Glyph(char_code)
    glyph.line_number = reader.line_number

    while True:
        line = reader.line()

        if line.startswith(u']'):
            break

        line = line.strip('\n')
        glyph.pointmap.append(list(line))

    glyph.args = args

    return glyph


def read_font_def(reader):
    '''Uses the given reader to generate Glyph objects.'''
    while True:
        line = reader.line()

        if line is None:
            break

        if line.startswith(u'#'):
            yield Comment(line[1:])

        if line.startswith(u'['):
            args = line[1:].split()

            if args[0] == '.notdef':
                char_code = -1
            else:
                char_code = int(args.pop(0).lstrip('Uu+'), 16)

            yield read_glyph(reader, char_code, args)


def get_font_def_filenames(dir_name):
    '''Return a list of glyph definition filenames.'''
    pattern = os.path.join(os.path.dirname(__file__), 'fonts', dir_name, '*',
        '*.kitabytedef')

    return list(glob.glob(pattern))
