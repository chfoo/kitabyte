# encoding=utf8
'''Kitabyte typeface font file build tools'''
# This file is part of Kitabyte.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under SIL OFL 1.1. See COPYING.txt for details.
import distutils.version

short_version = u'1.7'  # N.N
__version__ = short_version + u'.4'  # N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]

distutils.version.StrictVersion(__version__)
