#!/usr/bin/env python
from __future__ import generators
import sys
import os



# Some Python 3 compatibility shims
if sys.version_info.major < 3:
    STRING_TYPES = (str, unicode)
else:
    STRING_TYPES = str
    xrange = range

import keyword
# ^ keyword.kwlist is a list of all Python keywords.

from example.cpp.cpp import *

def no_collect(s, path, lineN):
    '''
    Sequential arguments:
    path -- the source code file path for tracing purposes.
    lineN -- the line number (starting with 1) for tracing purposes.
    '''
    sys.stdout.write(s)

def manualParse():
    from manualparser import ManualParser
    import ply.lex as lex
    lexer = lex.lex()
    import sys
    program = ManualParser()
    unchanged = False
    collect = program.collect
    program.showAll = True
    if unchanged:
        collect = no_collect
    for i in range(1, len(sys.argv)):
        path = sys.argv[i]
        with open(path) as f:
            stream = f.read()
            p = Preprocessor(lexer)
            p.parse(stream, sys.argv[i])
            indent = ""
            one_tab = "    "
            prevTok = None
            prevNWS = None  # previous non-whitespace token
            valueCloser = ""
            program.fromTokens(p)
    program.saveAs(None, stream=sys.stdout)

if __name__ == '__main__':
    # manualParse()
    # return

    import ply.lex as lex
    lexer = lex.lex()

    import sys

    p = Preprocessor(lexer)
    # print("sys.argv: {}".format(sys.argv))
    for i in range(1, len(sys.argv)):
        path = sys.argv[i]
        with open(path) as f:
            print("START parsing \"{}\"".format(path))
            input = f.read()
            # p = Preprocessor(lexer)
            p.parse(input, path)
            print("END parsing \"{}\"".format(path))
    if p.parser is None:
        print("No files were specified (or the parser wasn't"
              " initialized for some other reason).")
        exit(1)
    while True:
        tok = p.token()
        if not tok: break
        print(p.source, tok)
