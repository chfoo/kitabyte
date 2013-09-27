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
VISIBLE_CHARS = (u'x', u't', u'p', u'b', u'm')
SQUARE_SIZE = 25


class Builder(object):
    '''Uses Glyph objects to for drawing to FontForge.'''
    GlyphSizes = collections.namedtuple('GlyphSizes', [
        'square_size', 'descent_offset', 'row_len', 'row_count_flip',
    ])

    def __init__(self):
        super(Builder, self).__init__()
        self.font = None

    def _make_glyph(self, glyph_def):
        '''Creates a FontForge glyph using the given Glyph.'''
        font = self.font

        if glyph_def.char_code == -1:
            glyph = font.createChar(-1, '.notdef')
        else:
            glyph = font.createChar(glyph_def.char_code)

        glyph.clear()
        glyph.manualHints = True

        glyph_sizes = self._calc_glyph_sizes(glyph_def)

        self._draw_glyph_rows(glyph, glyph_def, glyph_sizes)
        self._add_anchors(glyph, glyph_def, glyph_sizes)

        for arg in glyph_def.args:
            if arg.startswith(u'reference:'):
                code = int(arg.split(u':', 1)[1].lstrip('uU+'), 16)
                glyph.addReference(fontforge.nameFromUnicode(code))
            elif arg.startswith(u'diacritic:'):
                code = int(arg.split(u':', 1)[1].lstrip('uU+'), 16)
                glyph.appendAccent(fontforge.nameFromUnicode(code))

#        if not ('oblique' in font.fontname.lower() or \
#        'bold' in font.fontname.lower()):
#            self._add_row_hints(glyph, glyph_def, glyph_sizes)
#            self._add_col_hints(glyph, glyph_def, glyph_sizes)

        if 'oblique' in font.fontname.lower():
            glyph.transform(psMat.skew(math.pi / 180 * 10), ('partialRefs',))

        if u'combining' in glyph_def.args:
            glyph.width = 0
        else:
            glyph.width = glyph_sizes.square_size * 8

    def _calc_glyph_sizes(self, glyph_def):
        '''Calculates and returns GlyphSizes for the given Glyph.'''
        square_size = SQUARE_SIZE
        descent_offset = self.font.descent + square_size
        row_len = len(glyph_def.bitmap)
        row_count_flip = 16

        return self.GlyphSizes(square_size, descent_offset, row_len,
            row_count_flip)

    def _draw_glyph_rows(self, glyph, glyph_def, glyph_sizes):
        '''Draws squares for creating the bitmap look.'''
        pen = glyph.glyphPen()

        for row in xrange(glyph_sizes.row_len):
            row_flip = glyph_sizes.row_count_flip - row

            for col in xrange(len(glyph_def.bitmap[row])):
                if glyph_def.bitmap[row][col] not in VISIBLE_CHARS:
                    continue

                if u'combining' in glyph_def.args:
                    col -= 8

                self._draw_square(pen, row_flip, col, glyph_sizes)

    def _add_anchors(self, glyph, glyph_def, glyph_sizes):
        '''Adds diacritic anchor points.'''
        for row in xrange(glyph_sizes.row_len):
            row_flip = glyph_sizes.row_count_flip - row
            y = row_flip * glyph_sizes.square_size - glyph_sizes.descent_offset

            for col in xrange(len(glyph_def.bitmap[row])):
                s = glyph_def.bitmap[row][col]
                x = col * glyph_sizes.square_size

                if s.lower() == u't':
                    glyph.addAnchorPoint('Top', 'base', x, y)
                elif s.lower() == u'p':
                    glyph.addAnchorPoint('Top', 'mark', x, y)
                elif s.lower() == u'b':
                    glyph.addAnchorPoint('Bottom', 'base', x, y)
                elif s.lower() == u'm':
                    glyph.addAnchorPoint('Bottom', 'mark', x, y)

    def _add_row_hints(self, glyph, glyph_def, glyph_sizes):
        '''Uses continuous blocks in a row as a hint.'''
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

    def _add_col_hints(self, glyph, glyph_def, glyph_sizes):
        '''Uses continuous blocks in a column as a hint.'''
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

    def _draw_square(self, pen, row, col, glyph_sizes):
        '''Draw a square by moving the pen.'''
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
        '''Builds the font file.'''
        self.font = font = fontforge.font()
    #    height = 32
        font.descent = 4 * SQUARE_SIZE
        font.ascent = 8 * SQUARE_SIZE
    #    font.em = 28
    #    font.design_size = 12
        font.upos = -2 * SQUARE_SIZE
        font.uwidth = SQUARE_SIZE
        font.fontname = fontname
        font.familyname = familyname
        font.fullname = fullname
        font.encoding = 'unicode'

        if 'bold' in fontname.lower():
            font.weight = 'Bold'

        if 'oblique' in fontname.lower():
            font.italicangle = -10.0

        if 'boldoblique' in fontname.lower():
            font.appendSFNTName(0x0409, 'SubFamily', 'Bold Oblique')

        font.addLookup('Anchors', 'gpos_mark2base', (), (
            ("mark", (("DFLT", ("dflt")),)),
        ))
        font.addLookupSubtable('Anchors', 'DiacriticTop')
        font.addAnchorClass('DiacriticTop', 'Top')
        font.addLookupSubtable('Anchors', 'DiacriticBottom')
        font.addAnchorClass('DiacriticBottom', 'Bottom')

        reader = Reader(
            *sorted(kitabyte.reader.get_font_def_filenames(dir_name)))

        deferred_glyph_defs = []

        for glyph_def in kitabyte.reader.read_font_def(reader):
            if isinstance(glyph_def, Glyph):
                try:
                    _logger.debug('Processing u+%x %s', glyph_def.char_code,
                        fontforge.nameFromUnicode(glyph_def.char_code))
                    self._make_glyph(glyph_def)
                except (EnvironmentError, ValueError):
                    _logger.debug('Deferring glyph u+%x %s',
                        glyph_def.char_code,
                        fontforge.nameFromUnicode(glyph_def.char_code))
                    deferred_glyph_defs.append(glyph_def)

        for glyph_def in deferred_glyph_defs:
            _logger.debug('Processing u+%x %s', glyph_def.char_code,
                    fontforge.nameFromUnicode(glyph_def.char_code))
            self._make_glyph(glyph_def)

        font.selection.all()
        font.removeOverlap()
        font.simplify()
        font.correctDirection()

        return font


COPYRIGHT_STR = (u'Copyright © 2012-2013 by Christopher Foo '
    '<chris.foo@gmail.com>. '
    u'Licensed under the SIL Open Font License version 1.1.'
)


def build_all(dest_dir_name, file_extensions=(u'sfd',)):
    '''Builds all the font files into given destination directory.'''
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
        font.copyright = COPYRIGHT_STR

        for file_extension in file_extensions:
            _logger.info('Building %s.%s', fontname, file_extension)
            font.generate(os.path.join(dest_dir_name,
                '%s.%s' % (fontname, file_extension)))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(u'dest_dir', default=os.path.curdir)
    arg_parser.add_argument(u'--format', default=[u'sfd'], nargs='*')

    args = arg_parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    build_all(args.dest_dir, args.format)
