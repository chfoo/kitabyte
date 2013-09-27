# encoding=utf8
'''Console-based file editor'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
import argparse
import gettext
import glob
import npyscreen
import os
import shutil

from kitabyte.font import Glyph
from kitabyte.reader import Reader, read_font_def, Comment
import collections


_ = gettext.gettext

# class Menu(object):
#     '''Simple menu.'''
#     def __init__(self, stdscr):
#         self._window = stdscr.newwin(2, 2)
#         self._panel = curses.panel.new_panel(self._window)
#         self._index = 0
#         self._options = []
#
#     def add_option(self, name, label):
#         '''Add an option.'''
#         self._options.append((name, label))
#
#     def show(self):
#         '''Show the menu and return the user selection.'''
#
#         self._panel.top()
#         self._panel.show()
#         self._window.clear()
#
#         while True:
#             self._window.refresh()
#             curses.doupdate()
#
#             key = self._window.getch()
#
# class Editor(object):
#     def __init__(self, path):
#         self._path = path
#         self._block_to_glyphs = {}
#         self._help = False
#         self._editor_pos = [0, 0]
#         self._current_block_name = None
#         self._current_glyph = None
#         self._key_table = {
#             curses.KEY_UP: self._move_cursor_up,
#             curses.KEY_DOWN: self._move_cursor_down,
#             curses.KEY_LEFT: self._move_cursor_left,
#             curses.KEY_RIGHT: self._move_cursor_right,
#             curses.KEY_HOME: self._set_cursor_left,
#             curses.KEY_END: self._set_cursor_right,
#             curses.KEY_PPAGE: self._set_cursor_top,
#             curses.KEY_NPAGE: self._set_cursor_bottom,
#             curses.KEY_F1: self._toggle_help,
#             curses.KEY_F9: self._show_prev,
#             curses.KEY_F10: self._show_next,
#             curses.KEY_F6: self._revert_file,
#             curses.KEY_F3: self._save_file,
#             # TODO: select block, jump to
#         }
#
#         curses.wrapper(self._initialized_cb)
#
#     def _initialized_cb(self, stdscr):
#         '''Star the program.'''
#         self._screen = stdscr
#         self._load_files()
#         self._run()
#
#     def _get_block_names(self):
#         '''Get the block names using the directory names.'''
#         iterable = glob.glob('{}/*'.format(self._path))
#         names = []
#         for name in iterable:
#             if os.path.isdir(name):
#                 names.append(name)
#
#         return names
#
#     def _load_files(self):
#         '''Load files.'''
#
#         for block_name in self._get_block_names():
#             iterable = glob.glob(
#                 '{}/{}/*.kitabytedef'.format(self._path, block_name))
#
#             self._block_to_glyphs[block_name] = []
#
#             for filename in sorted(iterable):
#                 glyphs = list(read_font_def(Reader(filename)))
#                 self._block_to_glyphs[block_name].append(glyphs[0])
#
#
#
#     def _seek_prev(self):
#         while True:
#             self._element_index -= 1
#
#             if self._element_index < 0:
#                 self._element_index = 0
#                 return False
#
#             if isinstance(self._elements[self._element_index], Glyph):
#                 self._load_glyph()
#                 return True
#
#     def _seek_forward(self):
#         while True:
#             self._element_index += 1
#
#             if self._element_index >= len(self._elements):
#                 self._element_index = len(self._elements) - 1
#                 return False
#
#             if isinstance(self._elements[self._element_index], Glyph):
#                 self._load_glyph()
#                 return True
#
#     def _load_glyph(self):
#         self._glyph_def = self._elements[self._element_index]
#         self._pointmap = self._glyph_def.pointmap
#
#     def _draw_all(self):
#         self._draw_glyph_info()
#         self._draw_editor()
#
#         if self._help:
#             self._draw_help()
#
#         self._screen.noutrefresh()
#
#         curses.doupdate()
#
#     def _draw_glyph_info(self):
#         self._screen.addstr(0, 0, u'Glyph u+%x %s Line %d' % (
#             self._glyph_def.char_code, u' '.join(self._glyph_def.args),
#             self._glyph_def.line_number))
#         self._screen.addch(curses.KEY_EOL)
#
#     def _draw_editor(self):
#         self._draw_glyph_rulers()
#         self._draw_glyph()
#
#     def _draw_glyph_rulers(self):
#         y, x = self._screen.getmaxyx()
#
#         for col in xrange(1, x // 2 - 1):
#             self._screen.addstr(1, col * 2, u'%2d' % col,
#                 curses.A_BOLD if col % 4 == 0 else 0)
#
#         for row in xrange(1, y - 2):
#             self._screen.addstr(1 + row, 0, u'%2d' % row,
#                 curses.A_BOLD if row % 4 == 0 else 0)
#
#     def _draw_glyph(self):
#         row_offset = 2
#         col_offset = 2
#
#         for row in xrange(len(self._pointmap)):
#             line = self._pointmap[row]
#
#             for col in xrange(len(line)):
#                 char = line[col]
#
#                 if char != u' ':
#                     flags = curses.A_REVERSE
#                 else:
#                     flags = 0
#
#                 self._screen.addstr(row_offset + row, col_offset + col * 2,
#                     u'%s%s' % (char, char), flags)
#
#     def _run(self):
#         while True:
#             self._draw_all()
#
#             row, col = self._editor_pos
#             self._screen.move(2 + row, 2 + col * 2 + 1)
#
#             c = self._screen.getch()
#
#             if c in self._key_table:
#                 self._key_table[c]()
#             elif curses.ascii.isprint(c):
#                 self._edit_pointmap(c)
#
#     def _move_cursor_left(self):
#         if self._editor_pos[1] > 0:
#             self._editor_pos[1] -= 1
#
#     def _move_cursor_right(self):
#         if self._editor_pos[1] < self._screen.getmaxyx()[1] // 2 - 2:
#             self._editor_pos[1] += 1
#
#     def _move_cursor_up(self):
#         if self._editor_pos[0] > 0:
#             self._editor_pos[0] -= 1
#
#     def _move_cursor_down(self):
#         if self._editor_pos[0] < self._screen.getmaxyx()[0] - 4:
#             self._editor_pos[0] += 1
#
#     def _set_cursor_left(self):
#         self._editor_pos[1] = 0
#
#     def _set_cursor_right(self):
#         self._editor_pos[1] = self._screen.getmaxyx()[1] // 2 - 2
#
#     def _set_cursor_top(self):
#         self._editor_pos[0] = 0
#
#     def _set_cursor_bottom(self):
#         self._editor_pos[0] = self._screen.getmaxyx()[0] - 4
#
#     def _edit_pointmap(self, c):
#         row, col = self._editor_pos
#
#         while len(self._pointmap) - 1 < row:
#             self._pointmap.append(u'')
#
#         self._pointmap[row] = edit_string(self._pointmap[row], col, chr(c))
#
#     def _toggle_help(self):
#         self._screen.erase()
#         self._help = not self._help
#
#     def _show_prev(self):
#         self._screen.erase()
#         self._seek_prev()
#
#     def _show_next(self):
#         self._screen.erase()
#         self._seek_forward()
#
#     def _draw_help(self):
#         help_win = self._screen.subwin(10, 40, 2, 2)
#         help_win.erase()
#
#         help_texts = (
#             u'F1 Toggle Help',
#             u'F3 Save',
#             u'F6 Revert',
#             u'F9 Previous Glyph',
#             u'F10 Next Glyph',
#         )
#
#         for i in xrange(len(help_texts)):
#             help_win.addstr(i + 1, 1, help_texts[i])
#
#         help_win.border()
#         help_win.touchwin()
#
#     def _revert_file(self):
#         self._load_file()
#         self._screen.erase()
#
#     def _save_file(self):
#         with open(self._filename + u'-new', 'w') as dest_file:
#             for element in self._elements:
#                 if isinstance(element, Glyph):
#                     element.clean_pointmap()
#                     dest_file.write('[ u+%x' % element.char_code)
#
#                     if element.args:
#                         dest_file.write(' ')
#                         dest_file.write(' '.join(element.args))
#
#                     dest_file.write('\n')
#
#                     for row in element.pointmap:
#                         dest_file.write(''.join(row))
#                         dest_file.write('\n')
#
#                     dest_file.write(']\n\n')
#
#                 elif isinstance(element, Comment):
#                     dest_file.write('#%s\n' % element.text.encode())
#
#         shutil.copy2(self._filename, self._filename + u'~')
#         os.rename(self._filename + u'-new', self._filename)


class App(npyscreen.NPSAppManaged):
    def __init__(self, path):
        self.path = path
        super(App, self).__init__()
        self.unicode_blocks = collections.OrderedDict()
        self._current_glyph = None
        self._current_glyph_index = 0
        self._current_block_name = None
        self._current_glyph_list = None

    def onStart(self):
        self._load_glyphs()
        self.addForm("MAIN", MainForm)
        self.addForm('unicode_block_selector', UnicodeBlockSelector)

    def set_unicode_block(self, name):
        main_form = self.getForm('MAIN')
        glyphs = self._current_glyph_list = self.unicode_blocks[name]
        self._current_glyph_index = 0
        self._current_glyph = glyphs[0]
        main_form.glyph_editor.set_glyph(self._current_glyph)

    def _get_unicode_block_names(self):
        iterable = glob.glob('{}/*'.format(self.path))
        names = []
        for name in sorted(iterable):
            if os.path.isdir(name):
                names.append(os.path.basename(name))

        return names

    def _load_glyphs(self):
        for block_name in self._get_unicode_block_names():
            iterable = glob.glob(
                '{}/{}/*.kitabytedef'.format(self.path, block_name))

            self.unicode_blocks[block_name] = []

            for filename in sorted(iterable):
                glyphs = list(read_font_def(Reader(filename)))
                self.unicode_blocks[block_name].extend(glyphs)

    def next_glyph(self):
        self._current_glyph_index += 1
        if self._current_glyph_index >= len(self._current_glyph_list):
            self._current_glyph_index = len(self._current_glyph_list) - 1

    def previous_glyph(self):
        self._current_glyph_index -= 1
        if self._current_glyph_index < 0:
            self._current_glyph_index = 0


class MainForm(npyscreen.FormBaseNewWithMenus):
    def create(self):
        self.name = _('Kitabyte Font File Editor')
        self._editor_menu = self.new_menu(name=_('Editor'))
        self._file_menu = self.new_menu(name=_('File'))

        self._editor_menu.addItemsFromList([
            ('Select Unicode Block', self._select_block_cb),
            ('Next Glyph', self._next_glyph_cb),
            ('Previous Glyph', self._previous_glyph_cb),
            ('Quit', self._exit_cb),
        ])

        self._file_menu.addItemsFromList([
            ('Save Glyph', self._save_cb),
            ('Revert Glyph', self._revert_cb),
        ])

        self.glyph_editor = self.add(GlyphEditor)

    def _exit_cb(self):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()

    def _select_block_cb(self):
        self.parentApp.switchForm('unicode_block_selector')

    def _next_glyph_cb(self):
        pass

    def _previous_glyph_cb(self):
        pass

    def _save_cb(self):
        pass

    def _revert_cb(self):
        pass


class GlyphEditor(npyscreen.BoxBasic):
    def __init__(self, *args, **kwargs):
        super(GlyphEditor, self).__init__(*args, **kwargs)
        self._dirty = False
        self._glyph = None
        self._render()

    def _render(self):
        if self._glyph:
            self._render_title()

        self.display()

    def _render_title(self):
        self.name = u'{}U+{:x} {}'.format(
            u'*' if self._dirty else '',
            self._glyph.char_code,
            u' '.join(self._glyph.args)
        )

    def set_glyph(self, glyph):
        self._glyph = glyph



class UnicodeBlockSelector(npyscreen.Popup):
    def create(self):
        self.name = _('Select Unicode Block')
        self._selection_widget = self.add(npyscreen.MultiLineAction,
            values=self.parentApp.unicode_blocks.keys())
        self._selection_widget.actionHighlighted = self.action_cb

    def afterEditing(self):
        self.parentApp.switchFormPrevious()

    def action_cb(self, act_on_this, key_press):
        self.parentApp.set_unicode_block(act_on_this)
        self.parentApp.switchFormPrevious()


def edit_string(s, index, new_str):
    l = list(s)

    if len(l) - 1 < index:
        l.extend([u' ' for dummy in xrange(index - (len(l) - 1))])

    l[index] = new_str

    return u''.join(l)


def main():
    default_path = os.path.join(os.path.dirname(__file__), 'fonts', 'regular')

    arg_parser = argparse.ArgumentParser(
        description=_('Kitabyte Font File Editor'))
    arg_parser.add_argument('path',
        default=default_path,
        help=_('The path of the font directory.'),
        nargs='?')

    args = arg_parser.parse_args()

    app = App(path=args.path)
    app.run()

if __name__ == '__main__':
    main()
