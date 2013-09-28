# encoding=utf8
'''Prints coverage report'''
# This file is part of Kitabyte.
# Copyright © 2012-2013 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
from __future__ import print_function

import collections
import os.path

from kitabyte.reader import Reader
import kitabyte.reader
import itertools


BlockInfo = collections.namedtuple('BlockInfo', ['name', 'start', 'end'])


def read_blocks_file():
    '''Reads and returns BlockInfo.'''
    path = os.path.join(os.path.dirname(__file__), 'data', 'Blocks.txt')

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            block_range, name = line.split(';', 1)
            name = name.strip()
            start_str, end_str = block_range.split('..', 1)
            start_int = int(start_str, 16)
            end_int = int(end_str, 16)

            yield BlockInfo(name, start_int, end_int)


BLOCK_INFOS = tuple(read_blocks_file())


def get_name(char_code):
    for info in BLOCK_INFOS:
        if info.start <= char_code <= info.end:
            return info.name


if __name__ == '__main__':
    counter = collections.Counter()

    reader = Reader(*kitabyte.reader.get_font_def_filenames('regular'))

    for glyph_def in kitabyte.reader.read_font_def(reader):
        name = get_name(glyph_def.char_code)
        counter[name] += 1

    for info in itertools.chain(BLOCK_INFOS, [BlockInfo(None, 0, 0)]):
        if counter[info.name]:
            num = counter[info.name]
            num_in_block = info.end - info.start + 1
            percent = float(num) / num_in_block * 100
            name = info.name if info.name else '.notdef'
            out_str = '{:30} {:4} {:4} {:8.02f}%'.format(name, num,
                num_in_block, percent)
            print(out_str)
