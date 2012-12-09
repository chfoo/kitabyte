# encoding=utf8
'''Text file reader'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
from kitabyte.font import Glyph
import glob
import os.path


def read_glyph(file_obj, char_code):
    glyph = Glyph(char_code)

    while True:
        line = file_obj.readline()

        if line.startswith(u']'):
            break

        glyph.bitmap.append([])

        line = line.strip('\n')

        for c in line:

            if c == u'x':
                glyph.bitmap[-1].append(True)
            else:
                glyph.bitmap[-1].append(False)

    if len(glyph.bitmap) != 16:
        raise Exception('Glyph %x height is not 16, was=%d, file=%s' % (
            char_code, len(glyph.bitmap), file_obj))

    return glyph


def read_font_def(file_obj):
    while True:
        line = file_obj.readline()

        if not line:
            break

        if line.startswith(u';'):
            continue

        if line.startswith(u'['):
            char_code = int(line[1:].strip(u' Uu+\n'), 16)

            yield read_glyph(file_obj, char_code)


def get_font_def_filenames(dir_name):
    pattern = os.path.join(os.path.dirname(__file__), 'fonts', dir_name,
        '*.kitabytedef')

    return list(glob.glob(pattern))
