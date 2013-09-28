#!/usr/bin/python
'''This script takes in files and writes out a file per glpyh.'''
# This file is part of Kitabyte.
# Copyright © 2013 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
import argparse
import os.path


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', nargs='+')

    args = arg_parser.parse_args()
    
    for def_filename in args.file:
        dest_dir = os.path.splitext(os.path.basename(def_filename))[0]
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
    
        with open(def_filename, 'rt') as in_file:
            out_file = None
            for line in in_file:
    #             print '>', line
                if line.startswith('['):
                    values = line.split()
                    filename = values[1].strip('.') + '.kitabytedef'
                    filename = os.path.join(dest_dir, filename)
                    out_file = open(filename, 'wb')
                    out_file.write(line)
                elif line.startswith(']'):
                    out_file.write(line)
                    out_file.close()
                    out_file = None
                elif out_file:
                    out_file.write(line)
