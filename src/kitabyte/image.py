# encoding=utf8
'''Generates glyph image sheet'''
# This file is part of Kitabyte.
# Copyright © 2013 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
import math

from kitabyte.reader import Reader
import kitabyte.reader


try:
    import cairo
    import pango
    import pangocairo
except ImportError:
    import warnings
    warnings.warn('Optional cairo/pango packages not installed.')


def make_sheet(columns=16, size=12):
    reader = Reader(*kitabyte.reader.get_font_def_filenames('regular'))
    glyphs = list(kitabyte.reader.read_font_def(reader))
    glyphs.sort(key=lambda x: x.char_code)
    num_glyphs = len(glyphs)

    rows = int(math.ceil(float(num_glyphs) / columns))

    padded_size = size + size // 2
    width = columns * padded_size
    height = rows * padded_size

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surf)
    pangocairo_context = pangocairo.CairoContext(context)
    font = pango.FontDescription("Kitabyte {}px".format(size))
#     font.set_absolute_size(size * pango.SCALE)
    layout = pangocairo_context.create_layout()
    layout.set_font_description(font)

    pangocairo_context.set_antialias(cairo.ANTIALIAS_NONE)
    context.set_antialias(cairo.ANTIALIAS_NONE)
    context.save()
    context.rectangle(0, 0, width, height)
    context.set_source_rgb(1, 1, 1)
    context.fill()
    context.restore()

    for column in xrange(columns):
        for row in xrange(rows):
            index = column + columns * row

            if index >= len(glyphs):
                break

            context.save()
            context.translate(column * padded_size, row * padded_size)
            glyph = glyphs[index]
            if glyph.char_code == -1:
                text = u''
            else:
                text = unichr(glyph.char_code)
            layout.set_text(text)
            pangocairo_context.update_layout(layout)
            pangocairo_context.show_layout(layout)
            context.restore()

    with open("build/kitabyte_sheet.png", "wb") as image_file:
        surf.write_to_png(image_file)

if __name__ == '__main__':
    make_sheet()
