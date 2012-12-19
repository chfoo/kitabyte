# encoding=utf8
'''Console-based file editor'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
from kitabyte.font import Glyph
from kitabyte.reader import Reader, Comment
import argparse
import base64
import curses
import curses.ascii
import kitabyte.reader
import os
import shutil


class Editor(object):
    def __init__(self, filename):
        self._filename = filename
        curses.wrapper(self._initialized_cb)

    def _initialized_cb(self, stdscr):
        self._stdscr = stdscr
        self._help = False
        self._editor_pos = [0, 0]
        self._key_table = {
            curses.KEY_UP: self._move_cursor_up,
            curses.KEY_DOWN: self._move_cursor_down,
            curses.KEY_LEFT: self._move_cursor_left,
            curses.KEY_RIGHT: self._move_cursor_right,
            curses.KEY_HOME: self._set_cursor_left,
            curses.KEY_END: self._set_cursor_right,
            curses.KEY_PPAGE: self._set_cursor_top,
            curses.KEY_NPAGE: self._set_cursor_bottom,
            curses.KEY_F1: self._toggle_help,
            curses.KEY_F9: self._show_prev,
            curses.KEY_F10: self._show_next,
            curses.KEY_F6: self._revert_file,
            curses.KEY_F3: self._save_file,
        }

        self._load_file()
        self._run()

    def _load_file(self):
        reader = Reader(self._filename)
        self._elements = list(kitabyte.reader.read_font_def(reader))
        self._element_index = -1
        self._seek_forward()

    def _seek_prev(self):
        while True:
            self._element_index -= 1

            if self._element_index < 0:
                self._element_index = 0
                return False

            if isinstance(self._elements[self._element_index], Glyph):
                self._load_glyph()
                return True

    def _seek_forward(self):
        while True:
            self._element_index += 1

            if self._element_index >= len(self._elements):
                self._element_index = len(self._elements) - 1
                return False

            if isinstance(self._elements[self._element_index], Glyph):
                self._load_glyph()
                return True

    def _load_glyph(self):
        self._glyph_def = self._elements[self._element_index]
        self._pointmap = self._glyph_def.pointmap

    def _draw_all(self):
        self._draw_glyph_info()
        self._draw_editor()

        if self._help:
            self._draw_help()

        self._stdscr.noutrefresh()

        curses.doupdate()

    def _draw_glyph_info(self):
        self._stdscr.addstr(0, 0, u'Glyph u+%x %s Line %d' % (
            self._glyph_def.char_code, u' '.join(self._glyph_def.args),
            self._glyph_def.line_number))
        self._stdscr.addch(curses.KEY_EOL)

    def _draw_editor(self):
        self._draw_glyph_rulers()
        self._draw_glyph()

    def _draw_glyph_rulers(self):
        y, x = self._stdscr.getmaxyx()

        for col in xrange(1, x // 2 - 1):
            self._stdscr.addstr(1, col * 2, u'%2d' % col,
                curses.A_BOLD if col % 4 == 0 else 0)

        for row in xrange(1, y - 2):
            self._stdscr.addstr(1 + row, 0, u'%2d' % row,
                curses.A_BOLD if row % 4 == 0 else 0)

    def _draw_glyph(self):
        row_offset = 2
        col_offset = 2

        for row in xrange(len(self._pointmap)):
            line = self._pointmap[row]

            for col in xrange(len(line)):
                char = line[col]

                if char != u' ':
                    flags = curses.A_REVERSE
                else:
                    flags = 0

                self._stdscr.addstr(row_offset + row, col_offset + col * 2,
                    u'%s%s' % (char, char), flags)

    def _run(self):
        while True:
            self._draw_all()

            row, col = self._editor_pos
            self._stdscr.move(2 + row, 2 + col * 2 + 1)

            c = self._stdscr.getch()

            if c in self._key_table:
                self._key_table[c]()
            elif curses.ascii.isprint(c):
                self._edit_pointmap(c)

    def _move_cursor_left(self):
        if self._editor_pos[1] > 0:
            self._editor_pos[1] -= 1

    def _move_cursor_right(self):
        if self._editor_pos[1] < self._stdscr.getmaxyx()[1] // 2 - 2:
            self._editor_pos[1] += 1

    def _move_cursor_up(self):
        if self._editor_pos[0] > 0:
            self._editor_pos[0] -= 1

    def _move_cursor_down(self):
        if self._editor_pos[0] < self._stdscr.getmaxyx()[0] - 4:
            self._editor_pos[0] += 1

    def _set_cursor_left(self):
        self._editor_pos[1] = 0

    def _set_cursor_right(self):
        self._editor_pos[1] = self._stdscr.getmaxyx()[1] // 2 - 2

    def _set_cursor_top(self):
        self._editor_pos[0] = 0

    def _set_cursor_bottom(self):
        self._editor_pos[0] = self._stdscr.getmaxyx()[0] - 4

    def _edit_pointmap(self, c):
        row, col = self._editor_pos

        while len(self._pointmap) - 1 < row:
            self._pointmap.append(u'')

        self._pointmap[row] = edit_string(self._pointmap[row], col, chr(c))

    def _toggle_help(self):
        self._stdscr.erase()
        self._help = not self._help

    def _show_prev(self):
        self._stdscr.erase()
        self._seek_prev()

    def _show_next(self):
        self._stdscr.erase()
        self._seek_forward()

    def _draw_help(self):
        help_win = self._stdscr.subwin(10, 40, 2, 2)
        help_win.erase()

        help_texts = (
            u'F1 Toggle Help',
            u'F3 Save',
            u'F6 Revert',
            u'F9 Previous Glyph',
            u'F10 Next Glyph',
        )

        for i in xrange(len(help_texts)):
            help_win.addstr(i + 1, 1, help_texts[i])

        help_win.border()
        help_win.touchwin()

    def _revert_file(self):
        self._load_file()
        self._stdscr.erase()

    def _save_file(self):
        with open(self._filename + u'-new', 'w') as dest_file:
            for element in self._elements:
                if isinstance(element, Glyph):
                    element.clean_pointmap()
                    dest_file.write('[ u+%x' % element.char_code)

                    if element.args:
                        dest_file.write(' ')
                        dest_file.write(' '.join(element.args))

                    dest_file.write('\n')

                    for row in element.pointmap:
                        dest_file.write(''.join(row))
                        dest_file.write('\n')

                    dest_file.write(']\n\n')

                elif isinstance(element, Comment):
                    dest_file.write('#%s\n' % element.text.encode())

        shutil.copy2(self._filename, self._filename + u'~')
        os.rename(self._filename + u'-new', self._filename)


def edit_string(s, index, new_str):
    l = list(s)

    if len(l) - 1 < index:
        l.extend([u' ' for dummy in xrange(index - (len(l) - 1))])

    l[index] = new_str

    return u''.join(l)


def main():
    arg_parser = argparse.ArgumentParser(
        description=u'Kitabyte Font file editor')
    arg_parser.add_argument('filename',
        help=u'The filename of the file for editing.')

    args = arg_parser.parse_args()

    Editor(args.filename)

if __name__ == '__main__':
    main()
