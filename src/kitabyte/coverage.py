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


def get_controls():
    '''Reads and returns control characters.'''
    path = os.path.join(os.path.dirname(__file__), 'data', 'controls.txt')

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            yield int(line, 16)


BLOCK_INFOS = tuple(read_blocks_file())
CONTROLS = frozenset(get_controls())


def get_name(char_code):
    '''Get the Unicode block name for given character code.'''
    for info in BLOCK_INFOS:
        if info.start <= char_code <= info.end:
            return info.name


def num_controls(block_info):
    '''Return the number of control characters within this block.'''
    counter = 0
    for control_int in CONTROLS:
        if block_info.start <= control_int <= block_info.end:
            counter += 1

    return counter


if __name__ == '__main__':
    counter = collections.Counter()

    reader = Reader(*kitabyte.reader.get_font_def_filenames('regular'))

    for glyph_def in kitabyte.reader.read_font_def(reader):
        name = get_name(glyph_def.char_code)
        counter[name] += 1

    for info in itertools.chain(BLOCK_INFOS, [BlockInfo(None, -1, -1)]):
        if counter[info.name]:
            num = counter[info.name]
            controls = num_controls(info)
            num_in_block = info.end - info.start + 1 - controls
            percent = float(num) / num_in_block * 100
            name = info.name if info.name else '.notdef'
            out_str = '{:30} {:6} {:6} {:6} {:8.02f}%'.format(name, num,
                num_in_block, controls, percent)
            print(out_str)
