# encoding=utf8
'''Font file building'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
from kitabyte.font import Glyph
from kitabyte.reader import Reader
import argparse
import collections
import fontforge
import kitabyte.reader
import logging
import math
import os.path
import psMat


_logger = logging.getLogger(__name__)
VISIBLE_CHARS = (u'x', u't', u'p')


class Builder(object):
    GlyphSizes = collections.namedtuple('GlyphSizes', [
        'square_size', 'descent_offset', 'row_len', 'row_count_flip',
    ])

    def make_glyph(self, glyph_def):
        font = self.font
        glyph = font.createChar(glyph_def.char_code)
        glyph.manualHints = True

        for arg in glyph_def.args:
            if arg.startswith(u'reference:'):
                code = int(arg.split(u':', 1)[1].lstrip('uU+'), 16)
                glyph.addReference(fontforge.nameFromUnicode(code))
            elif arg.startswith(u'diacritic:'):
                code = int(arg.split(u':', 1)[1].lstrip('uU+'), 16)
                glyph.appendAccent(fontforge.nameFromUnicode(code))

        glyph_sizes = self.calc_glyph_sizes(glyph_def)

        self.draw_glyph_rows(glyph, glyph_def, glyph_sizes)
        self.add_anchors(glyph, glyph_def, glyph_sizes)
        self.add_row_hints(glyph, glyph_def, glyph_sizes)
        self.add_col_hints(glyph, glyph_def, glyph_sizes)

        if u'combining' in glyph_def.args:
            glyph.width = 0
        else:
            glyph.width = 16

    def calc_glyph_sizes(self, glyph_def):
        square_size = 2
        descent_offset = self.font.descent + square_size
        row_len = len(glyph_def.bitmap)
        row_count_flip = 16

        return self.GlyphSizes(square_size, descent_offset, row_len, row_count_flip)

    def draw_glyph_rows(self, glyph, glyph_def, glyph_sizes):
        pen = glyph.glyphPen()

        for row in xrange(glyph_sizes.row_len):
            row_flip = glyph_sizes.row_count_flip - row

            for col in xrange(len(glyph_def.bitmap[row])):
                if glyph_def.bitmap[row][col] not in VISIBLE_CHARS:
                    continue

                if u'combining' in glyph_def.args:
                    col -= 8

                self.draw_square(pen, row_flip, col, glyph_sizes)

    def add_anchors(self, glyph, glyph_def, glyph_sizes):

        for row in xrange(glyph_sizes.row_len):
            row_flip = glyph_sizes.row_count_flip - row

            for col in xrange(len(glyph_def.bitmap[row])):
                s = glyph_def.bitmap[row][col]

                if s.lower() == u't':
                    glyph.addAnchorPoint('Top', 'base', col, row_flip)
                elif s.lower() == u'p':
                    glyph.addAnchorPoint('Top', 'mark', col, row_flip)

    def add_row_hints(self, glyph, glyph_def, glyph_sizes):
        l = []

        for row in xrange(glyph_sizes.row_len):
            row_flip = glyph_sizes.row_count_flip - row

            row_count = 0

            for col in xrange(len(glyph_def.bitmap[row])):
                if glyph_def.bitmap[row][col] not in VISIBLE_CHARS:
                    row_count = 0
                    continue

                row_count += 1

                if row_count == 3:
                    y = row_flip * glyph_sizes.square_size - \
                        glyph_sizes.descent_offset
                    l.append((y, glyph_sizes.square_size))

        glyph.hhints = tuple(reversed(l))

    def add_col_hints(self, glyph, glyph_def, glyph_sizes):
        l = []

        if not glyph_def.bitmap:
            return

        for col in xrange(max(len(row) for row in glyph_def.bitmap)):
            col_count = 0

            for row in xrange(glyph_sizes.row_len):
                try:
                    if glyph_def.bitmap[row][col] not in VISIBLE_CHARS:
                        col_count = 0
                        continue
                except IndexError:
                    col_count = 0
                    continue

                col_count += 1

                if col_count == 3:
                    x = col * glyph_sizes.square_size
                    l.append((x, glyph_sizes.square_size))

        glyph.vhints = l

    def draw_square(self, pen, row, col, glyph_sizes):
        square_size = glyph_sizes.square_size
        descent_offset = glyph_sizes.descent_offset
        x = col * square_size
        y = row * square_size - descent_offset

        if 'bold' in self.font.fontname.lower():
            x -= square_size * 0.5
            square_size *= 1.5

        pen.moveTo((x, y))
        pen.lineTo((x + square_size, y))
        pen.lineTo((x + square_size, y + square_size))
        pen.lineTo((x, y + square_size))
        pen.closePath()

    def build_font(self, dir_name, familyname, fontname, fullname):
        self.font = font = fontforge.font()
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

        reader = Reader(
            *sorted(kitabyte.reader.get_font_def_filenames(dir_name)))

        deferred_glyph_defs = []

        for glyph_def in kitabyte.reader.read_font_def(reader):
            if isinstance(glyph_def, Glyph):
                try:
                    _logger.debug('Processing u+%x %s', glyph_def.char_code,
                        fontforge.nameFromUnicode(glyph_def.char_code))
                    self.make_glyph(glyph_def)
                except:
                    _logger.exception('Deferring glyph u+%x %s',
                        glyph_def.char_code,
                        fontforge.nameFromUnicode(glyph_def.char_code))
                    deferred_glyph_defs.append(glyph_def)

        for glyph_def in deferred_glyph_defs:
            _logger.debug('Processing u+%x %s', glyph_def.char_code,
                    fontforge.nameFromUnicode(glyph_def.char_code))
            self.make_glyph(glyph_def)

        font.selection.all()
        font.removeOverlap()
        font.simplify()
        font.correctDirection()

        if 'oblique' in font.fontname.lower():
            font.transform(psMat.skew(math.pi / 180 * 10))

        return font


copyright_str = (u'Copyright © 2012-2013 by Christopher Foo '
    '<chris.foo@gmail.com>. '
    u'Licensed under the SIL Open Font License version 1.1.'
)


def build_all(dest_dir_name, file_extensions=(u'sfd',)):
    names = [
        (u'regular', u'Kitabyte', u'Kitabyte-Regular', u'Kitabyte',
            kitabyte.__version__),
        (u'regular', u'Kitabyte', u'Kitabyte-Bold', u'Kitabyte Bold',
            kitabyte.__version__),
        (u'regular', u'Kitabyte', u'Kitabyte-Oblique', u'Kitabyte Oblique',
            kitabyte.__version__),
        (u'regular', u'Kitabyte', u'Kitabyte-BoldOblique',
            u'Kitabyte Bold Oblique', kitabyte.__version__),
    ]

    builder = Builder()

    for dir_name, familyname, fontname, fullname, version in names:
        font = builder.build_font(dir_name, familyname, fontname, fullname)
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
