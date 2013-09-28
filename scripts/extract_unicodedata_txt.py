# encoding=utf8
'''Extracts the category field from a UnicodeData.txt.'''
# This file is part of Kitabyte.
# Copyright © 2013 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
from __future__ import print_function
import argparse

CONTROLS = ('Cc', 'Cf', 'Cs', 'Co', 'Cn',)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('path')

    args = arg_parser.parse_args()

    with open(args.path, 'r') as f:
        for line in f:
            fields = line.split(';')

            if fields[2] in CONTROLS:
                print(fields[0])
