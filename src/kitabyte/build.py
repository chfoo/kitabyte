# encoding=utf8
'''Font file building'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
from kitabyte.font import Glyph
from kitabyte.reader import Reader
import argparse
import fontforge
import kitabyte.reader
import logging
import os.path


_logger = logging.getLogger(__name__)


def make_glyph(font, glyph_def):
    glyph = font.createChar(glyph_def.char_code)
    glyph.manualHints = True

    for arg in glyph_def.args:
        if arg.startswith(u'reference:'):
            code = int(arg.split(u':', 1)[1].lstrip('uU+'), 16)
            glyph.addReference(fontforge.nameFromUnicode(code))
        elif arg.startswith(u'diacritic:'):
            code = int(arg.split(u':', 1)[1].lstrip('uU+'), 16)
            glyph.appendAccent(fontforge.nameFromUnicode(code))

    draw_glyph_rows(font, glyph, glyph_def)
    add_anchors(font, glyph, glyph_def)

    if u'combining' in glyph_def.args:
        glyph.width = 0
    else:
        glyph.width = 16


def draw_glyph_rows(font, glyph, glyph_def):
    square_size = 2
    descent_offset = font.descent + square_size

    pen = glyph.glyphPen()
    row_len = len(glyph_def.bitmap)

    for row in xrange(row_len):
#        row_flip = row_len - row
        row_flip = 16 - row

        for col in xrange(len(glyph_def.bitmap[row])):
            if glyph_def.bitmap[row][col] not in (u'x', u't', u'p'):
                continue

            if u'combining' in glyph_def.args:
                col -= 8

            draw_square(pen, row_flip, col, square_size, descent_offset)


def add_anchors(font, glyph, glyph_def):
    row_len = len(glyph_def.bitmap)

    for row in xrange(row_len):
#        row_flip = row_len - row
        row_flip = 16 - row

        for col in xrange(len(glyph_def.bitmap[row])):
            s = glyph_def.bitmap[row][col]

            if s.lower() == u't':
                glyph.addAnchorPoint('Top', 'base', col, row_flip)
            elif s.lower() == u'p':
                glyph.addAnchorPoint('Top', 'mark', col, row_flip)


def draw_square(pen, row, col, square_size, descent_offset):
    pen.moveTo((col * square_size,
        row * square_size - descent_offset))
    pen.lineTo((col * square_size + square_size,
        row * square_size - descent_offset))
    pen.lineTo((col * square_size + square_size,
        row * square_size + square_size - descent_offset))
    pen.lineTo((col * square_size,
        row * square_size + square_size - descent_offset))
    pen.closePath()


def build_font(dir_name, familyname, fontname, fullname):
    font = fontforge.font()
#    height = 32
    font.descent = 8
    font.ascent = 16
#    font.em = 28
#    font.design_size = 12
    font.upos = -4
    font.uwidth = 2
    font.fontname = fontname
    font.familyname = familyname
    font.fullname = fullname
    font.encoding = 'unicode'

    font.addLookup('Anchors', 'gpos_mark2base', (), (
        ("mark", (("DFLT", ("dflt")),)),
    ))
    font.addLookupSubtable('Anchors', 'DiacriticTop')
    font.addAnchorClass('DiacriticTop', 'Top')
#    font.addLookupSubtable('Anchors', 'DiacriticBottom')
#    font.addAnchorClass('DiacriticBottom', 'Bottom')

    reader = Reader(*sorted(kitabyte.reader.get_font_def_filenames(dir_name)))

    deferred_glyph_defs = []

    for glyph_def in kitabyte.reader.read_font_def(reader):
        if isinstance(glyph_def, Glyph):
            try:
                _logger.debug('Processing u+%x %s', glyph_def.char_code,
                    fontforge.nameFromUnicode(glyph_def.char_code))
                make_glyph(font, glyph_def)
            except:
                _logger.exception('Deferring glyph u+%x %s',
                    glyph_def.char_code,
                    fontforge.nameFromUnicode(glyph_def.char_code))
                deferred_glyph_defs.append(glyph_def)

    for glyph_def in deferred_glyph_defs:
        _logger.debug('Processing u+%x %s', glyph_def.char_code,
                fontforge.nameFromUnicode(glyph_def.char_code))
        make_glyph(font, glyph_def)

    font.selection.all()
    font.removeOverlap()
    font.simplify()
    font.correctDirection()
#    font.autoHint()

    return font


copyright_str = (u'Copyright © 2012 by Christopher Foo <chris.foo@gmail.com>. '
    u'Licensed under the SIL Open Font License version 1.1.'
)


def build_all(dest_dir_name, file_extensions=(u'sfd',)):
    names = [
        (u'regular', u'Kitabyte', u'Kitabyte-Regular', u'Kitabyte',
            kitabyte.__version__),
    ]

    for dir_name, familyname, fontname, fullname, version in names:
        font = build_font(dir_name, familyname, fontname, fullname)
        font.version = version
        font.copyright = copyright_str

        for file_extension in file_extensions:
            font.generate(os.path.join(dest_dir_name,
                '%s.%s' % (fontname, file_extension)))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(u'dest_dir', default=os.path.curdir)
    arg_parser.add_argument(u'--format', default=[u'sfd'], nargs='*')

    args = arg_parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    build_all(args.dest_dir, args.format)
